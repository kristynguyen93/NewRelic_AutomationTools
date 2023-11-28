import find_entities_not_reporting_deployments.find_entities_not_reporting_deployments as find_entities_not_reporting_deployments
import policies_and_conditions_report.policies_and_conditions_report as policies_and_conditions_report

def main():
    choice = 0
    menu_options = {
        1: "Find Entities Not Reporting Deployments",
        2: "Policies and Conditions Report",
        3: "Exit"
    }

    for option in menu_options:
        print(f"{option}: {menu_options[option]}")

    while choice != 3:
        choice = input("Enter your choice: ")

        try:
            choice = int(choice)
            if choice == 1:

                print("Generating Entities Not Reporting Deployments report... \n See logs.log for details.")

                find_entities_not_reporting_deployments.find_entities_not_reporting_deployment()

                file_name = find_entities_not_reporting_deployments.get_entities_filename()

                print("Report generated. See reports " + file_name + " in the output folder.")

            elif choice == 2:

                print("Generating policies and conditions report... \n See logs.log for details.")

                policies_and_conditions_report.generate_policies_conditions_report()

                policies_and_conditions_report_filename, invalid_policies_report_filename, empty_policies_report_filename = policies_and_conditions_report.get_report_file_names()

                print("Report generated. See reports " + policies_and_conditions_report_filename, invalid_policies_report_filename, empty_policies_report_filename + " in the output folder.")

            elif choice > 3:
                print("Please enter a valid choice.")

            elif choice == 3:
                print("Exiting application.")
                break

        except ValueError:
            print("Please enter a valid choice.")

if __name__ == '__main__':
    main()
