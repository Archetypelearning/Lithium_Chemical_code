class SetupTime:
    def __init__(self):
        self.tot_time = 0.0
        self.dt_minimum = 1.0e-7
        self.dt_maximum = 1.0e-3
        self.maximum_iteration = 1000
        self.dt_output = 1.0

    def get_user_input(self):
        print("Do you want to use the default values? (yes/no)")
        use_defaults = input("Do you want to use the default values? (yes/no) : ").strip().lower()
        
        if use_defaults == 'no':
            print("Enter total transient time (in seconds)")
            self.tot_time = float(input("Enter total transient time (in seconds) : "))

            print("Enter minimum time step size")
            self.dt_minimum = float(input("Enter minimum time step size : "))

            print("Enter maximum time step size ")
            self.dt_maximum = float(input("Enter maximum time step size : "))

            print(f"Enter time interval size for writing the output file is = {self.dt_output} s")
            self.maximum_iteration = int(input("Enter maximum number of iterations : "))

            print("Enter the time interval for writing the output file (in seconds) ")
            self.dt_output = float(input("Enter the time interval for writing the output file : "))

            print("\nUsing default values:")
            print(f"Total transient time is = {self.tot_time} s")
            print(f"dt_min is = {self.dt_minimum} s")
            print(f"dt_max is = {self.dt_maximum} s")
            print(f"Maximum number of iterations is = {self.maximum_iteration} #")
            print(f"Time interval for writing the output file is = {self.dt_output} s")
        else:
            print("Enter total transient time (in seconds)")
            self.tot_time = float(input("Enter total transient time (in seconds) : "))

            print("\nUsing default values:")
            print(f"Total transient time is = {self.tot_time} s")
            print(f"dt_min is = {self.dt_minimum} s")
            print(f"dt_max is = {self.dt_maximum} s")
            print(f"Maximum number of iterations is = {self.maximum_iteration} #")
            print(f"Time interval for writing the output file is = {self.dt_output} s")
