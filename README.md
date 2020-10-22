# Adobe Admin Console User CSV Parser
Danimae Vossen (2020)

This is a standalone application which will allow you to sort a CSV from the Adobe Admin Console (https://adminconsole.adobe.com).  To get a user list, please follow directions here:
http://helpx.adobe.com/enterprise/using/bulk-operations.html#Exportuserdata

"To download the user data, navigate to Users > Users in the Admin Console. Click  in the upper-right corner of the Users page, and choose Export users list to CSV."

When you get the CSV , it should have the following headers:

Identity Type
Username
Domain
Email
First Name
Last Name
Country Code
Product Configurations
Admin Roles
Product Configurations Administered
User Groups
User Groups Administered
Products Administered
Developer Access
Auto Assigned Products

The parser does not reuire all these fields, but at least the email field and the category you want to sort by.  To use the app, simply drop your CSV in the same folder as the EXE and double click.  You can also run from the command line to pass options directly.

```
Usage: aac_csv_parse.exe sort [OPTIONS]

  Sort a CSV.  This MUST be a csv downloaded from the Users tab, and nowhere
  else.

Options:
  -p, --path PATH
  -c, --category [product_profiles|admin_roles|products_profiles_administered|groups|groups_administered|products_administered|developer_access|auto_assigned_products]
  --help                          Show this message and exit.
```


If you do not a category on the command line, you will be prompted to select a category to sort by.  Choose the desired category with the arrow keys, and press enter:

Prompt:

![prompt](images\intro.jpg)

If you do not supply a path, a suggestion will be made based on the files in the current directory.  If the suggestion is not what you want, just enter the path to your users CSV file.

The tool will analyze and dump the users to a new csv, called `processed_ {CATEGORY}_{ORIGINAL_CSV_NAME}.csv`, and a summary to  `summary_ {CATEGORY}_{ORIGINAL_CSV_NAME}.txt`.  The process may take some time depending on the size of the user list.

The processed file will be a CSV, where the header indicates each category, and below it is a list of users in that category.  There will be one additional category, named 'no {CATEGORY}', where category is replaced by the category you selected.  In this column will be all users who did not have any entry in your specified category.

Example output:

![output](images\output.jpg)

Example summary:

![summary](images\summary.jpg)