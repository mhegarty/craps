# craps


This is a simulator for the table game craps.

You sould use conda for this...

Step 1) Setup a virtual environment. 
        >> cd path/to/root/folder/called/craps
	>>conda env create -n craps -f environment.yml
        >>activate craps

Step 2) Set up the Database... from cmd line:
	>>alembic revision --autogenerate
	>>alembic upgrade head

