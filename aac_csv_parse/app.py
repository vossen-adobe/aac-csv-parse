import csv
import os

import click
from click_default_group import DefaultGroup

class Category():
    def __init__(self, name, members):
        self.name = name
        self.members = members

    def pull_next(self):
        keys = list(self.members.keys())
        if keys:
            u = self.members.pop(keys[0])
            return u.email
        else:
            return ""


class User():

    def __init__(self,
                 type=None,
                 username=None,
                 domain=None,
                 email=None,
                 givenname=None,
                 surname=None,
                 country=None,
                 product_profs=None,
                 admin_roles=None,
                 products_profs_administered=None,
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
        self.product_profs = self.get_set(product_profs)
        self.admin_roles = self.get_set(admin_roles)
        self.products_profs_administered = self.get_set(products_profs_administered)
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
        for u in csv.DictReader(f):
            u = User.fromCSV(u)
            if u.type != 'federated id':
                u.email = "{0} ({1})".format(u.email, u.type)
            users[u.email] = u
    return users


def build_sorted_list(category, userlist):
    valid = User(email='xx')
    if not hasattr(valid, category):
        raise ValueError("Cannot sort by nonexistent property: {}".format(category))
    if not isinstance(getattr(valid, category), set):
        raise ValueError("Cannot categorize by non-list property: {}".format(category))
    non_cat = 'no {}'.format(category)
    cats = {non_cat: {}}
    for e, u in userlist.items():
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


def write_to_csv(cats, filename):
    cols = list(cats.keys())
    cols_ann = ["{0} ({1} users)".format(k, len(cats[k].members)) for k in cats.keys()]

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(cols_ann)

        c = 0
        while True:
            row = [cats[c].pull_next() for c in cols]
            if len(set(row)) == 1:
                break
            writer.writerow(row)
            if c % 1000 == 0:
                print(c)
            c += 1

@click.group(cls=DefaultGroup, default='sort', default_if_no_args=True)
@click.help_option('-h', '--help')
def main():
    pass

@main.command(help='')
@click.option('-p', '--path',default='users.csv', show_default=True)
def sort(path):
    filename = path.split(os.sep)[-1]
    path = os.path.abspath(path)
    dir = os.path.dirname(path)
    users = read_users(path)
    sorted = build_sorted_list('groups', users)
    write_to_csv(sorted, os.path.join(dir,'processed_{}'.format(filename)))

if __name__ == '__main__':
    main()
