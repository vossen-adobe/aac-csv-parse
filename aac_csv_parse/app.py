import csv
import os
from datetime import datetime

import click
import questionary
from click_default_group import DefaultGroup

class Category():
    def __init__(self, name, members):
        self.name = name
        self.members = members
        self.initial_count = self.size()

    def pull_next(self):
        keys = list(self.members.keys())
        if keys:
            u = self.members.pop(keys[0])
            return u.email
        else:
            return ""

    def size(self):
        return len(self.members)


class User():
    sortable_fields = [
        'product_profiles',
        'admin_roles',
        'products_profiles_administered',
        'groups',
        'groups_administered',
        'products_administered',
        'developer_access',
        'auto_assigned_products'
    ]

    def __init__(self,
                 type=None,
                 username=None,
                 domain=None,
                 email=None,
                 givenname=None,
                 surname=None,
                 country=None,
                 product_profiles=None,
                 admin_roles=None,
                 product_profiles_administered=None,
                 groups=None,
                 groups_administered=None,
                 products_administered=None,
                 developer_access=None,
                 auto_assigned_products=None):
        self.type = self.lower(type)
        self.username = self.lower(username)
        self.domain = self.lower(domain)
        self.email = self.lower(email)
        self.givenname = self.lower(givenname)
        self.surname = self.lower(surname)
        self.country = self.lower(country)
        self.product_profs = self.get_set(product_profiles)
        self.admin_roles = self.get_set(admin_roles)
        self.products_profs_administered = self.get_set(product_profiles_administered)
        self.groups = self.get_set(groups)
        self.groups_administered = self.get_set(groups_administered)
        self.products_administered = self.get_set(products_administered)
        self.developer_access = self.get_set(developer_access)
        self.auto_assigned_products = self.get_set(auto_assigned_products)

        if not self.email:
            raise ValueError("Email must not be blank")

    def lower(self, val):
        return str(val).lower() if val is not None else val

    def get_set(self, val):
        if not val:
            return set()
        return {v.lower() for v in val.split(',')}

    @classmethod
    def fromCSV(cls, fields):
        return cls(
            fields.get('Identity Type') or fields.get('ï»¿Identity Type'),
            fields.get('Username'),
            fields.get('Domain'),
            fields.get('Email'),
            fields.get('First Name'),
            fields.get('Last Name'),
            fields.get('Country Code'),
            fields.get('Product Configurations'),
            fields.get('Admin Roles'),
            fields.get('Product Configurations Administered'),
            fields.get('User Groups'),
            fields.get('User Groups Administered'),
            fields.get('Products Administered'),
            fields.get('Developer Access'),
            fields.get('Auto Assigned Products'),
        )


def read_users(filename):
    users = {}
    with open(filename) as f:
        for ud in csv.DictReader(f):
            try:
                u = User.fromCSV(ud)
            except ValueError:
                print('Error reading user - skipping.  Details: {}'.format(ud))
                continue
            if u.type != 'federated id':
                u.email = "{0} ({1})".format(u.email, u.type)
            users[u.email] = u
    return users


def build_sorted_list(category, user_list):
    if category not in User.sortable_fields:
        raise ValueError("Cannot categorize by non-list property: {}".format(category))

    non_cat = 'no {}'.format(category)
    cats = {non_cat: {}}
    for e, u in user_list.items():
        attr = getattr(u, category)
        if not attr:
            cats[non_cat][e] = u
            continue
        for c in attr:
            if c not in cats:
                cats[c] = {}
            cats[c][e] = u

    sorted_cats = {}
    for c, u in cats.items():
        sorted_cats[c] = {key: value for key, value in sorted(u.items())}
    return {key: Category(key, value) for key, value in sorted(sorted_cats.items())}


def write_to_csv(cats, data_filename):
    cols = list(cats.keys())
    cols_ann = ["{0} ({1} users)".format(k, cats[k].size()) for k in cats.keys()]
    max_rows = max([cats[k].size() for k in cats.keys()])

    with open(data_filename, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(cols_ann)

        c = 0
        while True:
            row = [cats[c].pull_next() for c in cols]
            if c % 1000 == 0 or len(set(row)) == 1:
                print("{0} / {1} ({2} %)".format(c, max_rows, round(100 * (c / max_rows), 2)))
            c += 1
            if len(set(row)) == 1:
                break
            writer.writerow(row)

def write_summary(summary_filename, total_users, outfile, sourcefile, category, sorted_dict):
    non_cat = 'no {}'.format(category)
    with open(summary_filename, 'w') as f:
        f.write('CSV analysis results:\n')
        f.write('-----------------------------------------\n')
        f.write('Completed on: {}\n'.format(datetime.now().strftime('%Y-%m-%d %H.%M.%S')))
        f.write('Parsed CSV: {}\n'.format(sourcefile))
        f.write('Sort category: {}\n'.format(category))
        f.write('Wrote full data to: {}\n'.format(outfile))
        f.write('Total users: {}\n'.format(total_users))
        f.write('Total users in {0}: {1}\n'.format(category, total_users - sorted_dict[non_cat].initial_count))
        f.write('Total without any {0}: {1}\n'.format(category, sorted_dict[non_cat].initial_count))
        f.write('\nPer {} counts: \n'.format(category))
        f.write('-----------------------------------------\n')
        f.write('# Users | Name\n')
        f.write('-----------------------------------------\n')
        for r, v in sorted_dict.items():
            f.write('{:<10}{}\n'.format(v.initial_count, r))
        f.write('-----------------------------------------\n')


@click.group(cls=DefaultGroup, default='sort', default_if_no_args=True)
@click.help_option('-h', '--help')
def main():
    pass



class QuestionaryOption(click.Option):

    def __init__(self, param_decls=None, **attrs):
        click.Option.__init__(self, param_decls, **attrs)
        if not isinstance(self.type, click.Choice):
            raise Exception('ChoiceOption type arg must be click.Choice')

    def prompt_for_value(self, ctx):
        val = questionary.select(self.prompt, choices=self.type.choices, default='groups').unsafe_ask()
        return val

@main.command(help='')
@click.option('-p', '--path',
              default=None,
              show_default=True,
              type=click.Path(exists=True))
@click.option('-c', '--category',
              prompt='Sort by which category: ',
              default='groups',
              type=click.Choice(User.sortable_fields, case_sensitive=False), cls=QuestionaryOption)
def sort(path, category):
    if path is None:
        path = click.prompt('Target CSV file',
                            default='users.csv',
                            show_default=True,
                            type=click.Path(exists=True))

    filename = path.split(os.sep)[-1]
    path = os.path.abspath(path)
    dir = os.path.dirname(path)
    data_output = os.path.join(dir, 'processed_{0}_{1}'.format(category, filename))
    summary_output = os.path.join(dir, 'summary_{0}_{1}'.format(category, filename))
    category = category.lower()

    print('Reading users: {}'.format(path))
    users = read_users(path)
    print('Total user records: {}'.format(len(users)))

    print("Assemble sorted dictionary by '{}'...".format(category))
    sorted = build_sorted_list(category, users)

    print('Process results to {}'.format(data_output))
    write_to_csv(sorted, data_output)

    print('Write summary to {}'.format(summary_output))
    write_summary(summary_output, len(users), data_output, path, category, sorted)
    print('-----------------------------------------')


if __name__ == '__main__':
    main()
