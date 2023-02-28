import mysql.connector.pooling
import tkinter as tk
import datetime
from prettytable import PrettyTable
from tkinter import messagebox#

# Define global variable for new window
new_window = None
single_record_window = None
records_frame = None # Define records_frame at the module level


# Create the main window
window = tk.Tk()
window.title("VR Referral Database")

# Create a connection pool to the MySQL database
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host="localhost",
    user="root",
    password="SQLBetastace11!",
    database="VR_Office"
)
def display_records(records, field_names, frame):
    # Clear the frame of any previous records
    for child in frame.winfo_children():
        child.destroy()

    # Create labels for the field names
    for i, field_name in enumerate(field_names):
        field_label = tk.Label(frame, text=field_name, font="bold")
        field_label.grid(row=0, column=i, padx=5, pady=5)

    # Create labels for each record
    for j, record in enumerate(records):
        for i, field_value in enumerate(record):
            record_label = tk.Label(frame, text=field_value)
            record_label.grid(row=j+1, column=i, padx=5, pady=5)

        # Add a "Select Record" button next to each record
        select_button = tk.Button(frame, text="Select Record", command=lambda id=record[0]: edit_record(id))
        select_button.grid(row=j+1, column=len(field_names), padx=5, pady=5)  
               
def edit_record(id):
    # Retrieve the record with the given ID from the database
    with pool.get_connection() as conn:
        cursor = conn.cursor(prepared=True)
        sql = "SELECT * FROM referrals WHERE id = %s"
        val = (id,)
        cursor.execute(sql, val)
        record = cursor.fetchone()
        cursor.close()

    # Create a new window for editing the record
    edit_window = tk.Toplevel(window)
    edit_window.title("Edit Referral Record")

    # Create input fields for each record field
    field_names = ["Date Entered", "Authorization Number", "CPWIC Name", "VRID Number", "Customer Name", "VR Unit Number", "Counselor", "Data/BSA Completed", "Authorization Date", "Comments", "Office Address", "Office City"]
    fields = {}

    for i, field_name in enumerate(field_names):
        field_label = tk.Label(edit_window, text=field_name)
        field_label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)

        field_entry = tk.Entry(edit_window, width=20)
        field_entry.grid(row=i, column=1, padx=5, pady=5)
        field_entry.insert(0, record[i])

        fields[field_name] = field_entry

    # Create a "Save Changes" button
    save_button = tk.Button(edit_window, text="Save Changes", command=lambda: save_changes(id, fields, edit_window))
    save_button.grid(row=len(field_names), column=1, padx=5, pady=5)

def save_changes(id, fields, edit_window):
    # Retrieve the values from the input fields
    values = [fields[field_name].get() for field_name in fields]

    # Update the record with the new values in the database
    with pool.get_connection() as conn:
        cursor = conn.cursor(prepared=True)
        sql = "UPDATE referrals SET date_entered = %s, authorization_number = %s, cpwic_name = %s, vrid_number = %s, customer_name = %s, vr_unit_number = %s, counselor = %s, data_bsa_completed = %s, authorization_date = %s, comments = %s, office_address = %s, office_city = %s WHERE id = %s"
        cursor.execute(sql, (*values, id))
        conn.commit()
        cursor.close()

    # Close the edit window
    edit_window.destroy()

#populate main screen vr office address and city
def update_vr_office_info(event):
    vrunit = vrunit_var.get()

    # Retrieve office address and city from the database
    with pool.get_connection() as conn:
        cursor = conn.cursor(prepared=True)
        sql = "SELECT address, city FROM vroffice WHERE unit = %s"
        val = (vrunit,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()

    if result:
        address, city = result
        address_entry.delete(0, tk.END)
        address_entry.insert(0, address)
        city_entry.delete(0, tk.END)
        city_entry.insert(0, city)
    else:
        address_entry.delete(0, tk.END)
        city_entry.delete(0, tk.END)

# View all records
def view_all_records():
    # Retrieve all referral records from the database
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM referrals")
        result = cursor.fetchall()
        cursor.close()

    # Get the field names for the pretty table
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'referrals'")
        field_names = [row[0] for row in cursor.fetchall()]
        cursor.close()

    # Create a pretty table to display the referral records
    table = PrettyTable()
    table.field_names = field_names

    for row in result:
        table.add_row(row)

    # Display the pretty table in a new window
    new_window = tk.Toplevel(window)
    new_window.title("All Referral Records")
    records_label = tk.Label(new_window, text=str(table))
    records_label.pack()


# Function to validate date
def validate_date(date_string):
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")

#Function to validate required field
def validate_required_field(value, field_name):
    if not value:
        raise ValueError(f"{field_name} is a required field")

# View all records
def view_all_records():
    # Retrieve all referral records from the database
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM referrals")
        result = cursor.fetchall()
        cursor.close()

    # Get the field names for the pretty table
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'referrals'")
        field_names = [row[0] for row in cursor.fetchall()]
        cursor.close()

    # Create a new window to display the referral records
    new_window = tk.Toplevel(window)
    new_window.title("All Referral Records")

    # Create a frame to display the referral records
    records_frame = tk.Frame(new_window)
    records_frame.grid(row=0, column=0)

    # Display the referral records in the frame
    display_records(result, field_names, records_frame)

    # Add navigation buttons for individual records
    num_records = len(result)
    index = 0

    def display_record(index):
        # Clear previous record, if any
        for child in records_frame.winfo_children():
            if isinstance(child, tk.Toplevel):
                child.destroy()

        # Create a new window for displaying the record
        single_record_window = tk.Toplevel(window)
        single_record_window.title("Referral Record")

        # Create labels for displaying the fields
        for i, field_name in enumerate(field_names):
            field_label = tk.Label(single_record_window, text=field_name)
            field_label.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)

            field_value = tk.Label(single_record_window, text=result[index][i])
            field_value.grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)

    def previous_record():
        nonlocal index
        if index > 0:
            index -= 1
            display_record(index)

    def next_record():
        nonlocal index
        if index < num_records - 1:
            index += 1
            display_record(index)

    prev_button = tk.Button(records_frame, text="Prev", command=previous_record)
    prev_button.grid(row=1, column=0, padx=5, pady=5)

    next_button = tk.Button(records_frame, text="Next", command=next_record)
    next_button.grid(row=1, column=1, padx=5, pady=5)


#Function to delete records
def delete_record():
    # Retrieve all referral records from the database
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM referrals")
        records = cursor.fetchall()
        cursor.close()

    # Create a new window to display the list of records to delete
    delete_window = tk.Toplevel(window)
    delete_window.title("Delete Referral Record")

    # Create a frame to display the list of records
    records_frame = tk.Frame(delete_window)
    records_frame.pack()

    # Create checkboxes for each record
    selected_records = []

    for i, record in enumerate(records):
        var = tk.IntVar()
        checkbox = tk.Checkbutton(records_frame, text=f"{record[1]} - {record[4]}", variable=var)
        checkbox.grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
        selected_records.append((record[0], var))

    # Create a button to delete the selected records
    def delete_selected_records():
        records_to_delete = [record[0] for record in selected_records if record[1].get() == 1]
        
        if records_to_delete:
            confirmation = messagebox.askyesno("Delete Records", f"Are you sure you want to delete {len(records_to_delete)} records?")
            
            if confirmation:
                with pool.get_connection() as conn:
                    cursor = conn.cursor()
                    placeholders = ', '.join(['%s'] * len(records_to_delete))
                    sql = f"DELETE FROM referrals WHERE id IN ({placeholders})"
                    cursor.execute(sql, records_to_delete)
                    conn.commit()
                    cursor.close()
                    
                messagebox.showinfo("Success", f"{len(records_to_delete)} records deleted.")
                delete_window.destroy()
                
        else:
            messagebox.showwarning("No Records Selected", "Please select at least one record to delete.")

    delete_button = tk.Button(delete_window, text="Delete Selected Records", command=delete_selected_records)
    delete_button.pack()

# Function to display all referral records
def view_all_records():
    # Retrieve all referral records from the database
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM referrals")
        records = cursor.fetchall()
        field_names = [column[0] for column in cursor.description]
        cursor.close()

    # Create a new window to display the referral records
    new_window = tk.Toplevel(window)
    new_window.title("All Referral Records")

    # Create a frame to display the referral records
    records_frame = tk.Frame(new_window)
    records_frame.pack()

    # Display the referral records in the frame
    display_records(records, field_names, records_frame)

# Function to insert referral record into MySQL database
def insert_referral_record():
    # Get user inputs
    try:
        validate_date(date_entry.get())
        validate_required_field(auth_entry.get(), "Authorization Number")
        validate_required_field(cust_entry.get(), "Customer Name")
        validate_required_field(vrunit_var.get(), "VR Unit Number")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    date_entered = date_entry.get()
    auth_num = auth_entry.get()
    cpwic_name = cpwic_entry.get()
    vrid_num = vrid_entry.get()
    cust_name = cust_entry.get()
    counselor = counselor_entry.get()
    data_bsa_completed = bsa_entry.get()
    auth_date = auth_date_entry.get()
    comments = comments_entry.get()
    vrunit = vrunit_var.get()
    vru_num = vrunit_var.get()

    # Retrieve office address and city from the database
    with pool.get_connection() as conn:
        cursor = conn.cursor(prepared=True)
        sql = "SELECT address, city FROM vroffice WHERE unit = %s"
        val = (vrunit,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()

    if result:
        address, city = result
    else:
        address, city = "", ""

    if not data_bsa_completed:
        data_bsa_completed = None

      # Insert referral record into MySQL database
    with pool.get_connection() as conn:
        cursor = conn.cursor(prepared=True)
        sql = "INSERT INTO referrals (date_entered, auth_num, cpwic_name, vrid_num, cust_name, vru_num, counselor, data_bsa_completed, auth_date, comments, office_address, office_city, vrunit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (date_entered, auth_num, cpwic_name, vrid_num, cust_name, vru_num, counselor, data_bsa_completed, auth_date, comments, address, city, vrunit)
        cursor.execute(sql, val)
        cursor.close()
        conn.commit()

    messagebox.showinfo("Success", "Referral record inserted.")

     # Clear input fields
    date_entry.delete(0, tk.END)
    auth_entry.delete(0, tk.END)
    cpwic_entry.delete(0, tk.END)
    vrid_entry.delete(0, tk.END)
    cust_entry.delete(0, tk.END)
    counselor_entry.delete(0, tk.END)
    bsa_entry.delete(0, tk.END)
    auth_date_entry.delete(0, tk.END)
    comments_entry.delete(0, tk.END)
    vrunit_var.set("")

    # Set focus to first input field
    date_entry.focus()

# Retrieve VR unit options from the database
with pool.get_connection() as conn:
    cursor = conn.cursor(prepared=True)
    cursor.execute("SELECT unit FROM vroffice")
    result = cursor.fetchall()
    cursor.close()

# Extract VR unit options from result
vrunit_options = [row[0] for row in result]


# Create GUI widgets
date_label = tk.Label(window, text="Date Entered")
date_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

today = datetime.date.today().strftime('%Y-%m-%d')
date_var = tk.StringVar(value=today)

def set_today():
    date_var.set(datetime.date.today().strftime('%Y-%m-%d'))
    date_entry.delete(0, tk.END)
    date_entry.insert(0, date_var.get())

date_entry = tk.Entry(window, width=20, textvariable=date_var)
date_entry.grid(row=0, column=1, padx=5, pady=5)

today_button = tk.Button(window, text="Today", command=set_today)
today_button.grid(row=0, column=2, padx=5, pady=5)




auth_label = tk.Label(window, text="Authorization Number")
auth_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
auth_entry = tk.Entry(window, width=20)
auth_entry.grid(row=1, column=1, padx=5, pady=5)

cpwic_label = tk.Label(window, text="CPWIC Name")
cpwic_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
cpwic_entry = tk.Entry(window, width=20)
cpwic_entry.grid(row=2, column=1, padx=5, pady=5)

vrid_label = tk.Label(window, text="VRID Number")
vrid_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
vrid_entry = tk.Entry(window, width=20)
vrid_entry.grid(row=3, column=1, padx=5, pady=5)

#vrunit_var = tk.StringVar(window)
#vrunit_var.set("Select VR Unit")

#vrunit_label = tk.Label(window, text="VR Unit")
#vrunit_label.grid(row=11, column=0)

#vrunit_dropdown = tk.OptionMenu(window, vrunit_var, *vrunit_options)
#vrunit_dropdown.config(width=20)
#vrunit_dropdown.grid(row=11, column=1, padx=5, pady=5)

cust_label = tk.Label(window, text="Customer Name")
cust_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
cust_entry = tk.Entry(window, width=20)
cust_entry.grid(row=4, column=1, padx=5, pady=5)

#vru_label = tk.Label(window, text="VR Unit Number")
#vru_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
#vru_entry = tk.Entry(window, width=20)
#vru_entry.grid(row=5, column=1, padx=5, pady=5)

counselor_label = tk.Label(window, text="Counselor Name")
counselor_label.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
counselor_entry = tk.Entry(window, width=20)
counselor_entry.grid(row=6, column=1, padx=5, pady=5)

bsa_label = tk.Label(window, text="Data/BSA Completed")
bsa_label.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
bsa_entry = tk.Entry(window, width=20)
bsa_entry.grid(row=7, column=1, padx=5, pady=5)

auth_date_label = tk.Label(window, text="Authorization Date")
auth_date_label.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)
auth_date_entry = tk.Entry(window, width=20)
auth_date_entry.grid(row=8, column=1, padx=5, pady=5)

address_label = tk.Label(window, text="VR Office Address")
address_label.grid(column=2, row=5, sticky=tk.W)
address_entry = tk.Entry(window, width=30)
address_entry.grid(column=3, row=5)

city_label = tk.Label(window, text="VR Office City")
city_label.grid(column=2, row=6, sticky=tk.W)
city_entry = tk.Entry(window, width=20)
city_entry.grid(column=3, row=6)


view_all_button = tk.Button(window, text="View All Records", command=view_all_records)
view_all_button.grid(column=3, row=11)

# Add button to view individual records
view_record_button = tk.Button(new_window, text="View Record", command=lambda: view_record(result, 0))

#delete button
delete_button = tk.Button(window, text="Delete Record", command=delete_record)
delete_button.grid(column=3, row=12)



comments_label = tk.Label(window, text="Comments")
comments_label.grid(column=2, row=8, sticky=tk.W)
comments_entry = tk.Entry(window, width=30)
comments_entry.grid(column=3, row=8)

# Add drop-down menu for VR unit selection
vrunit_var = tk.StringVar()
vrunit_label = tk.Label(window, text="VR Unit")
vrunit_label.grid(column=0, row=5, sticky=tk.W)
vrunit_dropdown = tk.OptionMenu(window, vrunit_var, *vrunit_options, command=lambda value: vrunit_var.set(value))
vrunit_dropdown.grid(column=1, row=5, sticky=tk.W)
vrunit_dropdown = tk.OptionMenu(window, vrunit_var, *vrunit_options, command=update_vr_office_info)
vrunit_dropdown.grid(column=1, row=5, sticky=tk.W)


# Add submit button
submit_button = tk.Button(window, text="Submit", command=insert_referral_record)
submit_button.grid(column=3, row=10)

# Set focus to first input field
date_entry.focus()

# Start the GUI
window.mainloop()
