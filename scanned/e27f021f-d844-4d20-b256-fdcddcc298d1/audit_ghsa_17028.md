# [H] phpMyFAQ SQL injections at insertentry & saveentry

## Summary
Severity: High
Advisory: GHSA-2grw-mc9r-822r
CVE: CVE-2024-28107
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-2grw-mc9r-822r
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=3.2.5 <3.2.6

## Details
### Summary
A SQL injection vulnerability has been discovered in the `insertentry` & `saveentry` when modifying records due to improper escaping of the email address. This allows any authenticated user with the rights to add/edit FAQ news to exploit this vulnerability to exfiltrate data, take over accounts and in some cases, even achieve RCE.

### PoC 1 - SQL Injection at insertentry:
1. Browse to “/admin/?action=editentry”, edit record and save. Intercept the POST request to "/admin/?action=insertentry" and modify the email and notes parameters in the body to the payloads below:
    a. `email=test'/*@email.com`
    b. `notes=*/,1,1,1,1,null,1);select+pg_sleep(5)--`

2. Send the request and notice the `pg_sleep(5)` command is executed with a time delay of 5 seconds in the response. This verifies that the SQL injection vulnerability exists.  
    ![image](https://github.com/thorsten/phpMyFAQ/assets/63487456/1000482f-3b00-462a-be8a-1eb21f720aca)

### PoC 2 - SQL Injection at saveentry
1. Browse to “/admin/?action=editentry”, edit record and save. Intercept the POST request to "/admin/?action=saveentry" and modify the email and notes parameters in the body to the payloads below:
    a. `email=test'/*@email.com`
    b. `*/,notes=(select+pg_sleep(5))--`
 2. Send the request and notice the `pg_sleep(5)` command is executed with a time delay of 5 seconds in the response. This verifies that the SQL injection vulnerability exists.
    ![image](https://github.com/thorsten/phpMyFAQ/assets/63487456/b1880ad1-1461-4735-9a67-9aa4d6c19b13)


### Impact
The SQL injection vulnerability discovered allows authenticated users with appropriate privileges to execute malicious SQL queries, potentially leading to data exfiltration, account takeover, and even remote code execution. Attackers can exploit the vulnerability to read sensitive data from the database, such as user credentials and system files, compromising the confidentiality and integrity of the system. Moreover, successful exploitation may enable attackers to gain unauthorized access to user accounts or execute arbitrary commands on the server, impacting both system administrators and end users.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-2grw-mc9r-822r
- https://nvd.nist.gov/vuln/detail/CVE-2024-28107
- https://github.com/thorsten/phpMyFAQ/commit/d0fae62a72615d809e6710861c1a7f67ac893007
- https://github.com/thorsten/phpMyFAQ
