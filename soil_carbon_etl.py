import os
import csv
import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from dto import Location, Profile, Orgc, Orgcmethod
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


logging.basicConfig(filename='pipeline.log', level=logging.INFO)

__author__  = "Brian Pondi"
__status__  = "Development"

class SoilCarbonPipeline:
    
    def __init__(self, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME) -> None:
        # Set up the database engine and session
        self.engine = create_engine(f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.metadata = MetaData()
        self.location : Location = None
        self.profile : Profile = None
        self.orgcmethod : Orgcmethod = None
        self.orgc : Orgc = None

    def _populate_location_table(self, row) -> Location:
        if not self.metadata.exists(self.engine, 'location'):
            # Check if the location already exists in the database
            location = self.session.query(Location).filter_by(x=row['X'], y=row['Y']).first()
        if location is None:
            # Create a new location object
            location = Location(x=row['X'], y=row['Y'], country_name=row['country_name'])
        return location

    def _populate_profile_table(self, row) -> Profile:
        if not self.metadata.exists(self.engine, 'profile'):
            # Check if the profile already exists in the database
            profile = self.session.query(Profile).filter_by(profile_layer_id=row['profile_layer_id']).first()
        if profile is None:
            # Create a new profile object
            profile = Profile(
            location_id = self.location.id,
            profile_layer_id = row['profile_layer_id'],
            upper_depth = row['upper_depth'],
            lower_depth = row['lower_depth'],
            layer_name = row['layer_name']
        )
        return profile

    def _populate_orgcmethod_table(self,row) -> Orgcmethod:
        # preprocess the orgc methods
        methods = row['orgc_method']
        methods = (str(methods)[2:-2]).split(",")
        orgc_methods_list =[]
        for method in methods:
            data = (method.split("="))[1]
            orgc_methods_list.append(data)
        calculation, detection, reaction, sample_pretreatment, temperature, treatment = orgc_methods_list
        if not self.metadata.exists(self.engine, 'orgcmethod'):
            # Check if the orgc method already exists in the database
            orgcmethod = self.session.query(Orgcmethod).filter_by(calculation=calculation, reaction=reaction, treatment= treatment).first()
        if orgcmethod is None:
            # Create a new orgcmethod object
            orgcmethod = Orgcmethod(
                calculation = calculation,
                detection = detection,
                reaction = reaction,
                sample_pretreatment = sample_pretreatment,
                temperature = temperature
            )
        return orgcmethod

    def _populate_orgc_table(self, row) -> Orgc:
        if not self.metadata.exists(self.engine, 'orgc'):
            # Check if the orgc value already exists in the database
            orgc = self.session.query(Orgc).filter_by(orgc_value=row['orgc_value'],orgc_dataset_id=row['orgc_dataset_id'], orgc_profile_code=row['orgc_profile_code']).first()
        if orgc is None:
            # Create a new orgc object
            orgc = Orgc(
                profile_id = self.profile.id,
                orgcmethod_id = self.orgcmethod.id,
                orgc_value_avg = row['orgc_value_avg'],
                orgc_dataset_id = row['orgc_dataset_id'],
                orgc_profile_code = row['orgc_profile_code']
                )
        return orgc

    def read_process_save_data_to_db(self, CSV_PATH) -> None:
        self.session 
        # Create the tables
        Base.metadata.create_all(self.engine)
        # Read the data from the CSV file
        with open(f'{CSV_PATH}') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.location = self._populate_location_table(row)
                self.profile = self._populate_profile_table(row)
                self.orgcmethod = self._populate_orgcmethod_table(row)
                self.orgc = self._populate_orgc_table(row)      
        
                # Add the objects to the session
                self.session.add(self.location)
                self.session.add(self.profile)
                self.session.add(self.orgcmethod)
                self.session.add(self.orgc)

                # Commit the changes to the database
                self.session.commit()
        logging.info('The session is coming to a close')
        self.session.close()


def main():
    DB_USERNAME = os.environ['PG_USER']
    DB_PASSWORD  = os.environ['PG_PASSWORD']
    DB_HOST = os.environ['PG_HOST']
    DB_PORT = os.environ['PG_PORT']
    DB_NAME =  os.environ['PG_DB_NAME']

    CSV_PATH = './data/data_belgium.csv'

    pipeline = SoilCarbonPipeline(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    pipeline.read_process_save_data_to_db(CSV_PATH)



    logging.info('==========================The process is complete=============================')
    logging.info('------------------------------------------------------------------------------')

if __name__ == '__main__':
    main()