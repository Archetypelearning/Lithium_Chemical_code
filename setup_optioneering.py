class SetupOptioneering:
    def __init__(self):
        self.domain_choice = 0
        self.transient_choice = 0
        self.coeff_choice = 0

    def prompt_user(self):
        # Prompt for domain shape
        print("\nSelect the domain shape for the chemical interactions from the following options:")
        print("1. Cubic")
        print("2. Cylindrical")
        print("3. Hemispherical")
        print("4. Hemisphere + Cylinder")

        self.domain_choice = input("Enter the number corresponding to your choice (1, 2, 3, or 4): ")
        print("Your choice is =", self.domain_choice, "\n")

        # Prompt for transient type
        print("\nDefine whether the leak is steady state or time dependent: ")
        print("1. S.S (boundary condition keep constant with time, unique values)")
        print("2. T.D (boundary condition changes with respect to time, time series data imported from .xlsx file)")

        self.transient_choice = input("Enter the number corresponding to your choice (1 or 2): ")
        print("Your choice is =", self.transient_choice, "\n")

        # Prompt for reaction rate coefficient calculation method
        print("\nSelect the reaction rate coefficient (k) calculation option:")
        print("1. Arrhenius equation vs Temperature")
        print("2. Linear extrapolation vs Temperature")
        print("3. Exponential extrapolation vs Temperature")

        self.coeff_choice = input("Enter the number corresponding to your choice (1, 2 or 3): ")
        print("Your choice is =", self.coeff_choice, "\n")


