# packages needed
import pandas as pd # loading the datafiles
from math import radians, sin, cos, atan2, sqrt # advanced math to calculate distance between coordinates

# needed to import the files from google drive
from google.colab import drive
drive.mount('/content/drive')

# Shortened list of vaccines
vaccine_abbreviations = [
    "BCG",  # Bacille Calmette-Guérin
    "OPV",  # Oral Polio Vaccine
    "IPV",  # Inactivated Polio Vaccine
    "DTP",  # Diphtheria, Tetanus, Pertussis
    "HepB",  # Hepatitis B
    "MMR",  # Measles, Mumps, Rubella
    "Rotavirus",
    "PCV",  # Pneumococcal Conjugate Vaccine
    "TT",  # Tetanus Toxoid
    "YFV",  # Yellow Fever Vaccine
]

# Dictionary mapping abbreviations to full names
vaccine_dictionary = {
    "BCG": "Bacille Calmette-Guérin",
    "OPV": "Oral Polio Vaccine",
    "DTP": "Diphtheria, Tetanus, Pertussis",
    "HepB": "Hepatitis B",
    "MMR": "Measles, Mumps, Rubella",
    "Rotavirus": "Rotavirus",
    "PCV": "Pneumococcal Conjugate Vaccine",
    "IPV": "Inactivated Polio Vaccine",
    "YFV": "Yellow Fever Vaccine",
    "TT": "Tetanus Toxoid",
}

# recommended year range for each vaccine
vaccine_age_recommendations_years_int = {
    "BCG": (0, 35),
    "OPV": (0, 6),
    "DTP": (0, 2),
    "HepB": (0, 2),
    "MMR": (1, 2),
    "Rotavirus": (0, 1),
    "PCV": (0, 2),
    "IPV": (0, 2),
    "YFV": (1, 10),
    "TT": (0, 6),
}

# Import hospitals
hospitals = pd.read_excel('/content/drive/My Drive/subset_sub-saharan_health_facilities_edited.xlsx')# you will probably store it in the same place, so no changes should be necessary

# Import citizens
citizens = pd.read_excel('/content/drive/My Drive/citizens_angola_Bengo.xlsx')  # you will probably store it in the same place, so no changes should be necessary

# subsets to work with (the files i sent you guys are already subset, but keep this part of the code to showcase)
hospitals_subset = hospitals[(hospitals['Country'] == 'Angola') & (hospitals['City'] == 'Bengo')]
citizens_subset = citizens.head(39000)

# here is how the df look for Hospitals
hospitals_subset.head(5)

# here is how the df look for Citizens
citizens_subset.head(5)

# calculate distance between two pairs of coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (sin(dlat / 2) ** 2) + cos(radians(lat1)) * cos(radians(lat2)) * (sin(dlon / 2) ** 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# Loop through citizens and find the nearest hospital, (Nearest_Hospital and Distance_to_Nearest_Hospital)
for index_citizen, citizen in citizens_subset.iterrows():
    distances = {}

    # Calculate distances for all hospitals for the current citizen
    for index_hospital, hospital in hospitals_subset.iterrows():
        distance = haversine(citizen['Lat'], citizen['Long'], hospital['Lat'], hospital['Long'])
        distances[hospital['Facility Name']] = distance

    # Find the nearest hospital for the current citizen
    min_distance_hospital = min(distances, key=distances.get)
    min_distance_value = distances[min_distance_hospital]

    # Assign the nearest hospital and distance to the citizens_subset DataFrame
    citizens_subset.at[index_citizen, 'Nearest_Hospital'] = min_distance_hospital
    citizens_subset.at[index_citizen, 'Distance_to_Nearest_Hospital'] = min_distance_value

# Count Citizens belonging to each hospital
hospitals_subset['Citizens'] = hospitals_subset['Facility Name'].apply(lambda hospital_name: citizens_subset['Nearest_Hospital'].eq(hospital_name).sum()
)

# count number of citizens in the relevant age range for each vaccine, then count number of vaccinated and not vaccinated
for vaccine, age_range in vaccine_age_recommendations_years_int.items():
    # Filter individuals within the age range for the vaccine
    eligible_individuals = citizens_subset[
        (citizens_subset['Age'] >= age_range[0]) & (citizens_subset['Age'] <= age_range[1])
    ]

    for index, hospital in hospitals_subset.iterrows():
        # Count total relevant population for the hospital
        vaccine_hospital_tot_count = len(eligible_individuals[eligible_individuals['Nearest_Hospital'] == hospital['Facility Name']])

        # Count the number of citizens who have taken the vaccine
        vaccinated_count = eligible_individuals[(eligible_individuals['Nearest_Hospital'] == hospital['Facility Name']) & (eligible_individuals[vaccine] == 1)].shape[0]

        # Count the number of citizens who have not taken the vaccine
        not_vaccinated_count = vaccine_hospital_tot_count - vaccinated_count

        # Add new columns to hospitals_subset for the current vaccine
        hospitals_subset.at[index, f'{vaccine}_Citizen_Count'] = vaccine_hospital_tot_count
        hospitals_subset.at[index, f'{vaccine}_Vaccinated_Count'] = vaccinated_count
        hospitals_subset.at[index, f'{vaccine}_Not_Vaccinated_Count'] = not_vaccinated_count


# here is how the df look now

# first lets check the Hospitals here we now have citizens in the rigth age range and if their vaccinated

bcg_columns = hospitals_subset.filter(like='BCG')
selected_columns = ['Country', 'City', 'Facility Name'] + list(bcg_columns.columns)
subset_with_bcg_columns = hospitals_subset[selected_columns]
subset_with_bcg_columns

# now lets check the citizens subset
citizens_subset.head(5)

# ask for the hospital of the worker
my_hospital = 'Hospital Provincial de Bengo'
patients_subset = []
# making a class, the class can also convert df with patients/citizens
class Patient:
  all_IDs = []
  all_countries = []
  all_cities = []

  # Possible vaccines
  possible_vaccines = [v.upper() for v in vaccine_abbreviations]

  # Vaccine dictionary
  vaccine_description = vaccine_dictionary

  # default input
  def __init__(self, ID, age, gender, hospital=my_hospital, df=None):
    self.ID = ID
    self.age = age
    self.gender = gender
    self.hospital = hospital
    self.vaccine_status = {}
    Patient.all_IDs.append(ID)

    # Access DataFrame to get additional information (to have less input work from health worker)
    if df is None:
      hospital_info = hospitals_subset[hospitals_subset['Facility Name'] == hospital].iloc[0]
      self.city = hospital_info['City']
      self.country = hospital_info['Country']
      Patient.all_countries.append(hospital_info['Country'])
      Patient.all_cities.append(hospital_info['City'])
      self.add_to_citizens_subset()
    else:
      patient_info = df[df['ID'] == ID].iloc[0]
      self.city = patient_info['City']
      self.country = patient_info['Country']
      Patient.all_countries.append(patient_info['Country'])
      Patient.all_cities.append(patient_info['City'])

    # Set vaccination status based on DataFrame information
      self.set_vaccination_status_from_df(patient_info)

    patients_subset.append(self)

  def add_to_citizens_subset(self):
    global citizens_subset
    new_patient_info = {'ID': self.ID, 'Age': self.age, 'Gender': self.gender, 'City': self.city, 'Country': self.country}
    citizens_subset = citizens_subset.append(new_patient_info, ignore_index=True)

  def set_vaccination_status_from_df(self, patient_info):
    # Extract relevant columns from DataFrame
    vaccine_columns = patient_info.index[patient_info.index.isin(vaccine_abbreviations)]

    # Set vaccination status based on DataFrame information
    for vaccine in vaccine_columns:
      self.vaccine_status[vaccine.upper()] = bool(patient_info[vaccine])


  def get_vaccines_list(self):
    return self.vaccine_description

  def input_vaccination_status(self, **kwargs):
    expected_vaccines = {vaccine.upper() for vaccine in self.get_not_true_vaccines()}

    for vaccine_name, status in kwargs.items():
      if vaccine_name.upper() in expected_vaccines:
        self.vaccine_status[vaccine_name.upper()] = status
      else:
        print(f"Ignoring unknown vaccine: {vaccine_name}")

    # Update vaccination status in citizens_subset
      self.update_citizens_subset_vaccination_status()

  def update_citizens_subset_vaccination_status(self):
    global citizens_subset
    # Find the patient in citizens_subset and update their vaccination status
    row_index = citizens_subset.loc[citizens_subset['ID'] == self.ID].index[0]
    for vaccine, status in self.vaccine_status.items():
      citizens_subset.at[row_index, vaccine] = int(status)


    # get the vaccines the child has taken
  def get_true_vaccines(self):
    true_keys = []
    for key, value in self.vaccine_status.items():
      if value == True:
        true_keys.append(key)
    return true_keys

  # get the vaccines the child misses
  def get_not_true_vaccines(self):
    missing_vaccines = []
    for vaccine in self.possible_vaccines:
      if vaccine not in self.get_true_vaccines():
        missing_vaccines.append(vaccine)
      else: pass
    return missing_vaccines

  def summary(self):
    print(f'Patient with ID {self.ID} has birth gender {self.gender}. This patient has age {self.age} and lives in {self.city}.\nThe patient has at current time taken these vaccines: {self.get_true_vaccines()}\nVaccines that are missing: {self.get_not_true_vaccines()}')

# adding the df to the class
patients_subset = [Patient(ID=row['ID'], age=row['Age'], gender=row['Gender'], df=citizens_subset) for _, row in citizens_subset.iterrows()]

# Function to find a patient by ID
def find_patient_by_id(target_id:int, patients_list=patients_subset):
    for patient in patients_list:
        if patient.ID == target_id:
            return patient  # Return the patient instance if found
    return None  # Return None if no patient with the specified ID is found

# okay lets check if the patient from the data frame we loaded is of the class Patients
cool_human =  find_patient_by_id(2)
cool_human.summary()

# Start the interface: Are you working at a Hospital or for the Goverment?
def initial_interface():
    print("Hi, please specify if you work at a hospital or for the Government.")
    valid_choice = False
    while valid_choice == False:
      choice = input("Type 'H' for Hospital or 'G' for Government: ").upper()

      if choice == 'H':
        valid_choice = True
        hospital_menu()
      elif choice == 'G':
        valid_choice = True
        government_menu()
      else:
        print("Invalid choice. Please input a valid answer.")


# If at hospitals, this will be the next step
def hospital_menu():
    message = f"""\nHi, what would you like to do?\n  A. Get a report on a patient\n  B. Add a patient\n  C. Update vaccine status"""
    print(message)
    choice = input("Enter your choice: ").upper()

    # get report on a patient
    if choice == 'A':
        get_report()

    # add patient
    elif choice == 'B':
        add_new_patient()

    # C. update vaccine status
    elif choice == 'C':
        valid_ID = False
        while valid_ID == False:
          patient_id = int(input("Enter the patient ID: "))
          patient_at_hand = find_patient_by_id(patient_id)

          #If the provided ID is not yet registered, then either register the patient or give up another ID.
          if patient_at_hand == None:
            message = f"""This patient is not yet registered. What would you like to do?\n  A. Add a new patient with this ID\n  B. Update the vaccination status of another patient\n"""
            print(message)
            choice = input("Choice: ").upper()
            if choice == "A":
              valid_ID = True
              add_new_patient()
            elif choice == "B":
              pass
          else:
            valid_ID = True
            set_vaccine_status(patient_at_hand)

    else:
        print("Invalid choice. Please input a valid answer.")
        hospital_menu()

def government_menu():
    message = f"""\nWhat would you like to do?\n  A. Add citizens\n  B. Distribute vaccines\n  C. Get overall report\n"""
    print(message)

    choice = input("Enter your choice: ").upper()

    if choice == 'A':
        add_citizens()
    elif choice == 'B':
        distribute_vaccines()
    elif choice == 'C':
        get_overall_report()
    else:
        print("Invalid choice. Please input a valid answer.")
        government_menu()

######################################################
###### FUNCTIONS USED IN THE HOSPITAL INTERFACE ######
######################################################

# add a new patient
def add_new_patient():
  print('I can help you with that, please provide me with ID, age and gender of the patient and the hospital you are currently at.')
  ID_exists = True

  while ID_exists == True:
    ID_input = int(input('ID:'))

    #If the ID is already in our Patient class, then we cannot add another patient with this ID.
    if ID_input in Patient.all_IDs:
      print("This ID is already registered. Please provide another ID.")
    else:
      ID_exists = False
      age_input = int(input('Age in whole number:'))
      gender_input = input('F for female or M for Male:').upper()
      hospital_input = input('The Hospital Facility Name: ')
      patient_at_hand = Patient(ID = ID_input, age = age_input, gender = gender_input, hospital = hospital_input)

      # also add vaccines for the new patient?
      print('Thank you. Would you also like to update the vaccine status of the patient you added?')
      update_vaccines = input('Type "Yes" to update or "No" if not needed: ').upper()

      # if yes this will happen
      if update_vaccines == 'YES':
        set_vaccine_status(patient_at_hand)

      # if No we pass
      else: pass

# get report
def get_report():
  valid_ID = False

  while valid_ID == False:
    patient_id = int(input("Enter the patient ID: "))
    patient = find_patient_by_id(patient_id)

    #If the provided ID is not yet registered, then either register the patient or give up another ID.
    if patient == None:
      message = f"""This patient is not yet registered. What would you like to do?\n  A. Add a new patient with this ID\n  B. Get a report on another patient\n"""
      print(message)
      choice = input("Choice: ").upper()
      if choice == "A":
        valid_ID = True
        add_new_patient()
      elif choice == "B":
        pass
    else:
      valid_ID = True
      print(patient.summary())

# set_vaccine_status
def set_vaccine_status(patient_at_hand):

    print(f'As of now your patient has taken the following vaccines: {patient_at_hand.get_true_vaccines()}.\nYou will need to input the short name of the vaccines you want to update the status on.\nDo you need the list of short names with their description?')
    # do you need a list of the short name you should input?
    need_list = input('Type "Yes" to update or "No" if not needed. ').upper()
    if need_list == 'YES':
        print(patient_at_hand.get_vaccines_list())
    else:
        pass

    vaccine_list_true = input('Please provide a list of the vaccines that the patient has taken, the list should be short names separated by a comma. ')

    if ',' in vaccine_list_true:
    # Split the input string into a list and convert each element to uppercase
        vaccine_list_true = [vaccine.strip().upper() for vaccine in vaccine_list_true.split(',')]
        kwargs = {vaccine: True for vaccine in vaccine_list_true}

    else:
    # If there's no comma, assume a single vaccine name and convert it to uppercase
        vaccine_list_true = vaccine_list_true.strip().upper()
        kwargs = {vaccine_list_true: True}

    patient_at_hand.input_vaccination_status(**kwargs)
    print(f'Thank you for updating the vaccine status of your patient, patient: {patient_at_hand.ID} has now taken the current vaccines: {patient_at_hand.get_true_vaccines()}')

########################################################
###### FUNCTIONS USED IN THE GOVERNMENT INTERFACE ######
########################################################

### OPTION C: GET A REPORT

# Function to choose a country and see whether it is in the datalist.
def get_overall_report():
  list_countries = list(dict.fromkeys(Patient.all_countries)) #This gives list of all countries without duplicates
  list_cities = list(dict.fromkeys(Patient.all_cities)) #This gives a list of all cities without duplicates

  message = f"""You chose to get a vaccination report. What country do you want to get a report on?\n"""
  print(message)
  valid_country = False

  #Check whether the country is in the list of possible countries.
  while valid_country == False:
    country_input = input("Country: ")

    if country_input in list_countries:
      valid_country = True
      message = f"""This is the report for {country_input}:\n"""
      print(message)
      country_report(country_input)
    else:
      message = f"""This country is not in the datalist that was provided. Please pick another country.\n"""
      print(message)

# Function that gives general metrics on the entire country and asks if more detail is needed.
def country_report(country_input):

  #How many hospitals are there in this country?
  list_hospitals = hospitals_subset['Facility Name'][hospitals_subset['Country']==country_input].tolist()
  hospitals_count = len(list_hospitals)

  #How many cities are there in this country?
  full_list_cities = citizens_subset['City'][citizens_subset['Country']==country_input].tolist()
  list_cities = list(dict.fromkeys(full_list_cities))
  cities_count = len(list_cities)

#How many patients are there in this country that are eligible for at least one vaccine? list_ID's will have all ID's (no duplicates) of patients eligible for at least 1 vaccine.
  full_list_IDs = []
  vaccines_country = {} #this dictionary will contain all vaccines as keys, and a list [#vaccinated, #eligible]

  # For every vaccine, we will calculate how many eligible patients there are in the given country, as well as the coverage rate among these patients.
  for vaccine, age_range in vaccine_age_recommendations_years_int.items():
    eligible_individuals = citizens_subset[(citizens_subset['Age'] >= age_range[0]) & (citizens_subset['Age'] <= age_range[1]) & (citizens_subset['Country']==country_input)]
    list_elig = eligible_individuals['ID'].tolist()
    elig_count = len(list_elig)
    elig_vaccinated = 0

    for index, row in eligible_individuals.iterrows():
      full_list_IDs.append(row['ID'])
      elig_vaccinated += row[vaccine]

    coverage_rate = round(elig_vaccinated/elig_count,4)
    vaccines_country[vaccine] = [elig_vaccinated,elig_count,coverage_rate]
  print(vaccines_country)

  list_IDs = list(dict.fromkeys(full_list_IDs))
  patients_count = len(list_IDs)

  message = f"""{country_input} has {cities_count} cities and {hospitals_count} hospitals.\nIn total, {patients_count} patients are in the appropriate age range for at least 1 routine vaccine.\n"""
  print(message)

  valid_answer = False
  while valid_answer == False:
    message2 = f"""Do you want to get a more detailed report? If so, what would you like to specify on?\n  A. This report was sufficient.\n  B. Specify a city\n  C. Specify a vaccine\n  D. Specify a hospital\n"""
    print(message2)

    answer = input("Answer: ").upper()

    if answer == "A":
      valid_answer = True
      pass

    elif answer == "B":
      valid_answer = True
      print(f"""Which city would you like a report on?\n""")
      city = input("City: ") #needs to check whether this city is in the city list for this country.
      city_report(city)

    elif answer == "C":
      valid_answer = True
      print(f"""Which vaccine would you like a report on?\n""")
      vaccine = input("Vaccine: ")
      vaccine_report(vaccine) #needs to check whether this vaccine is in the vaccine list.

    elif answer == "D":
      valid_answer = True
      print(f"""Which hospital would you like a report on?\n""")
      hospital = input("Hospital: ")
      hospital_report(hospital) #needs to check whether this vaccine is in the vaccine list.

    else:
      print("Please provide a valid answer.")

def city_report(city):
  message = f"""This is a more detailed report for {city}:\n"""
  print(message)

def vaccine_report(vaccine):
  message = f"""This is a more detailed report for the {vaccine} vaccine:\n"""
  print(message)

def hospital_report(hospital):
  message = f"""This is a more detailed report for {hospital}:\n"""
  print(message)

def add_citizens():
  print("You chose the option 'add citizens'")

def distribute_vaccines():
  print("You chose the option 'Distribute vaccines'")

# Start the interface: Are you working at a Hospital or for the Goverment?
def initial_interface():
    print("Hi, please specify if you work at a hospital or for the Government.")
    valid_choice = False
    while valid_choice == False:
      choice = input("Type 'H' for Hospital or 'G' for Government: ").upper()

      if choice == 'H':
        valid_choice = True
        hospital_menu()
      elif choice == 'G':
        valid_choice = True
        government_menu()
      else:
        print("Invalid choice. Please input a valid answer.")


# If at hospitals, this will be the next step
def hospital_menu():
    message = f"""\nHi, what would you like to do?\n  A. Get a report on a patient\n  B. Add a patient\n  C. Update vaccine status"""
    print(message)
    choice = input("Enter your choice: ").upper()

    # get report on a patient
    if choice == 'A':
        get_report()

    # add patient
    elif choice == 'B':
        add_new_patient()

    # C. update vaccine status
    elif choice == 'C':
        valid_ID = False
        while valid_ID == False:
          patient_id = int(input("Enter the patient ID: "))
          patient_at_hand = find_patient_by_id(patient_id)

          #If the provided ID is not yet registered, then either register the patient or give up another ID.
          if patient_at_hand == None:
            message = f"""This patient is not yet registered. What would you like to do?\n  A. Add a new patient with this ID\n  B. Update the vaccination status of another patient\n"""
            print(message)
            choice = input("Choice: ").upper()
            if choice == "A":
              valid_ID = True
              add_new_patient()
            elif choice == "B":
              pass
          else:
            valid_ID = True
            set_vaccine_status(patient_at_hand)

    else:
        print("Invalid choice. Please input a valid answer.")
        hospital_menu()

def government_menu():
    message = f"""\nWhat would you like to do?\n  A. Add citizens\n  B. Distribute vaccines\n  C. Get overall report\n"""
    print(message)

    choice = input("Enter your choice: ").upper()

    if choice == 'A':
        add_citizens()
    elif choice == 'B':
        distribute_vaccines()
    elif choice == 'C':
        get_overall_report()
    else:
        print("Invalid choice. Please input a valid answer.")
        government_menu()

######################################################
###### FUNCTIONS USED IN THE HOSPITAL INTERFACE ######
######################################################

# add a new patient
def add_new_patient():
  print('I can help you with that, please provide me with ID, age and gender of the patient and the hospital you are currently at.')
  ID_exists = True

  while ID_exists == True:
    ID_input = int(input('ID:'))

    #If the ID is already in our Patient class, then we cannot add another patient with this ID.
    if ID_input in Patient.all_IDs:
      print("This ID is already registered. Please provide another ID.")
    else:
      ID_exists = False
      age_input = int(input('Age in whole number:'))
      gender_input = input('F for female or M for Male:').upper()
      hospital_input = input('The Hospital Facility Name: ')
      patient_at_hand = Patient(ID = ID_input, age = age_input, gender = gender_input, hospital = hospital_input)

      # also add vaccines for the new patient?
      print('Thank you. Would you also like to update the vaccine status of the patient you added?')
      update_vaccines = input('Type "Yes" to update or "No" if not needed: ').upper()

      # if yes this will happen
      if update_vaccines == 'YES':
        set_vaccine_status(patient_at_hand)

      # if No we pass
      else: pass

# get report
def get_report():
  valid_ID = False

  while valid_ID == False:
    patient_id = int(input("Enter the patient ID: "))
    patient = find_patient_by_id(patient_id)

    #If the provided ID is not yet registered, then either register the patient or give up another ID.
    if patient == None:
      message = f"""This patient is not yet registered. What would you like to do?\n  A. Add a new patient with this ID\n  B. Get a report on another patient\n"""
      print(message)
      choice = input("Choice: ").upper()
      if choice == "A":
        valid_ID = True
        add_new_patient()
      elif choice == "B":
        pass
    else:
      valid_ID = True
      print(patient.summary())

# set_vaccine_status
def set_vaccine_status(patient_at_hand):

    print(f'As of now your patient has taken the following vaccines: {patient_at_hand.get_true_vaccines()}.\nYou will need to input the short name of the vaccines you want to update the status on.\nDo you need the list of short names with their description?')
    # do you need a list of the short name you should input?
    need_list = input('Type "Yes" to update or "No" if not needed. ').upper()
    if need_list == 'YES':
        print(patient_at_hand.get_vaccines_list())
    else:
        pass

    vaccine_list_true = input('Please provide a list of the vaccines that the patient has taken, the list should be short names separated by a comma. ')

    if ',' in vaccine_list_true:
    # Split the input string into a list and convert each element to uppercase
        vaccine_list_true = [vaccine.strip().upper() for vaccine in vaccine_list_true.split(',')]
        kwargs = {vaccine: True for vaccine in vaccine_list_true}

    else:
    # If there's no comma, assume a single vaccine name and convert it to uppercase
        vaccine_list_true = vaccine_list_true.strip().upper()
        kwargs = {vaccine_list_true: True}

    patient_at_hand.input_vaccination_status(**kwargs)
    print(f'Thank you for updating the vaccine status of your patient, patient: {patient_at_hand.ID} has now taken the current vaccines: {patient_at_hand.get_true_vaccines()}')

########################################################
###### FUNCTIONS USED IN THE GOVERNMENT INTERFACE ######
########################################################

### OPTION C: GET A REPORT

# Function to choose a country and see whether it is in the datalist.
def get_overall_report():
  list_countries = list(dict.fromkeys(Patient.all_countries)) #This gives list of all countries without duplicates
  list_cities = list(dict.fromkeys(Patient.all_cities)) #This gives a list of all cities without duplicates

  message = f"""You chose to get a vaccination report. What country do you want to get a report on?\n"""
  print(message)
  valid_country = False

  #Check whether the country is in the list of possible countries.
  while valid_country == False:
    country_input = input("Country: ")

    if country_input in list_countries:
      valid_country = True
      message = f"""This is the report for {country_input}:\n"""
      print(message)
      country_report(country_input)
    else:
      message = f"""This country is not in the datalist that was provided. Please pick another country.\n"""
      print(message)

# Function that gives general metrics on the entire country and asks if more detail is needed.
def country_report(country_input):

  #How many hospitals are there in this country?
  list_hospitals = hospitals_subset['Facility Name'][hospitals_subset['Country']==country_input].tolist()
  hospitals_count = len(list_hospitals)

  #How many cities are there in this country?
  full_list_cities = citizens_subset['City'][citizens_subset['Country']==country_input].tolist()
  list_cities = list(dict.fromkeys(full_list_cities))
  cities_count = len(list_cities)

#How many patients are there in this country that are eligible for at least one vaccine? list_ID's will have all ID's (no duplicates) of patients eligible for at least 1 vaccine.
  full_list_IDs = []
  vaccines_country = {} #this dictionary will contain all vaccines as keys, and a list [#vaccinated, #eligible]

  # For every vaccine, we will calculate how many eligible patients there are in the given country, as well as the coverage rate among these patients.
  for vaccine, age_range in vaccine_age_recommendations_years_int.items():
    eligible_individuals = citizens_subset[(citizens_subset['Age'] >= age_range[0]) & (citizens_subset['Age'] <= age_range[1]) & (citizens_subset['Country']==country_input)]
    list_elig = eligible_individuals['ID'].tolist()
    elig_count = len(list_elig)
    elig_vaccinated = 0

    for index, row in eligible_individuals.iterrows():
      full_list_IDs.append(row['ID'])
      elig_vaccinated += row[vaccine]

    coverage_rate = round(elig_vaccinated/elig_count,4)
    vaccines_country[vaccine] = [elig_vaccinated,elig_count,coverage_rate]
  print(vaccines_country)

  list_IDs = list(dict.fromkeys(full_list_IDs))
  patients_count = len(list_IDs)

  message = f"""{country_input} has {cities_count} cities and {hospitals_count} hospitals.\nIn total, {patients_count} patients are in the appropriate age range for at least 1 routine vaccine.\n"""
  print(message)

  valid_answer = False
  while valid_answer == False:
    message2 = f"""Do you want to get a more detailed report? If so, what would you like to specify on?\n  A. This report was sufficient.\n  B. Specify a city\n  C. Specify a vaccine\n  D. Specify a hospital\n"""
    print(message2)

    answer = input("Answer: ").upper()

    if answer == "A":
      valid_answer = True
      pass

    elif answer == "B":
      valid_answer = True
      print(f"""Which city would you like a report on?\n""")
      city = input("City: ") #needs to check whether this city is in the city list for this country.
      city_report(city)

    elif answer == "C":
      valid_answer = True
      print(f"""Which vaccine would you like a report on?\n""")
      vaccine = input("Vaccine: ")
      vaccine_report(vaccine) #needs to check whether this vaccine is in the vaccine list.

    elif answer == "D":
      valid_answer = True
      print(f"""Which hospital would you like a report on?\n""")
      hospital = input("Hospital: ")
      hospital_report(hospital) #needs to check whether this vaccine is in the vaccine list.

    else:
      print("Please provide a valid answer.")

def city_report(city):
  message = f"""This is a more detailed report for {city}:\n"""
  print(message)

def vaccine_report(vaccine):
  message = f"""This is a more detailed report for the {vaccine} vaccine:\n"""
  print(message)

def hospital_report(hospital):
  message = f"""This is a more detailed report for {hospital}:\n"""
  print(message)

def add_citizens():
  print("You chose the option 'add citizens'")

def distribute_vaccines():
  print("You chose the option 'Distribute vaccines'")


# function to start the interface

# check for hospital A
initial_interface()

# check for hospital B
hospital_interface()

# check that the df is updated
citizens_subset[citizens_subset['ID']==101]

# check trough the class as well
test = find_patient_by_id(101)
test.get_true_vaccines()




##### STREAMLIT HERE #####

import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def hospital_menu():
    st.write("\nHospital Menu:")
    choice = st.selectbox("Select an option:", ["Get a Report", "Add a Patient", "Update Vaccine Status"])
  
    if choice == "Get a Report":
        st.write("Hospital: Getting a report...")
    elif choice == "Add a Patient":
        st.write("Hospital: Adding a patient...")
    elif choice == "Update Vaccine Status":
        st.write("Hospital: Updating vaccine status...")
  
  
def government_menu():
    st.write("\nGovernment Menu:")
    choice = st.selectbox("Select an option:", ["Add Citizens", "Distribute Vaccines", "Get Overall Report"])
  
    if choice == "Add Citizens":
        st.write("Government: Adding citizens...")
    elif choice == "Distribute Vaccines":
        st.write("Government: Distributing vaccines...")
    elif choice == "Get Overall Report":
        st.write("Government: Getting overall report...")

def run():

  st.title("Vaccination app")
  
  user_type = st.radio("Select your user type:", ["Hospital", "Government"])
  
  if user_type == "Hospital":
      st.title("Hospital Vaccination App")
  
      # Add a button to proceed after selecting user type
      if st.button("Continue"):
          # Call the hospital_menu function
          hospital_menu()
  
  elif user_type == "Government":
      st.title("Government Vaccination App")
  
      # Add a button to proceed after selecting user type
      if st.button("Continue"):
          # Call the government_menu function
          government_menu()
  


if __name__ == "__main__":
    run()
