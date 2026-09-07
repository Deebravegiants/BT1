# [H] phpMyFAQ SQL Injection at "Save News"

## Summary
Severity: High
Advisory: GHSA-qgxx-4xv5-6hcw
CVE: CVE-2024-27299
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-qgxx-4xv5-6hcw
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=3.2.5 <3.2.6

## Details
### Summary
A SQL injection vulnerability has been discovered in the the "Add News" functionality due to improper escaping of the email address. This allows any authenticated user with the rights to add/edit FAQ news to exploit this vulnerability to exfiltrate data, take over accounts and in some cases, even achieve RCE.

### Details
The vulnerable field lies in the  `authorEmail` field which uses PHP's `FILTER_VALIDATE_EMAIL` filter. This filter is insufficient in protecting against SQL injection attacks and should still be properly escaped. However, in this version of phpMyFAQ (3.2.5), this field is not escaped properly can be used together with other fields to fully exploit the SQL injection vulnerability.

### PoCs
4 PoCs are demonstrated here to illustrate the potential impacts.

#### PoC 1 - Postgres Time Based SQLi
1. Login as admin or any user with the rights to view and save news.
2. Navigate to "../phpmyfaq/admin/?action=news", click on "Add news", fill in some data, send and intercept the request.
3. Modify the intercepted "/admin/?action=save-news" request to look like the SS below:
    3.1 - Set the "authorEmail" field in the body to "`test'/*@[email.com](http://email.com/)`".
    3.2 - Set the "linkTitle" field in the body to "`*/,1,1,1,1,1,1,1);select+pg_sleep(5)--`".
    3.3 - Set the rest of the fields as empty and send the request.
4. Notice the 5s delay in the response time, indicating that the sleep function was executed, verifying the existence of the SQLi vulnerability.
![image](https://github.com/thorsten/phpMyFAQ/assets/63487456/b19a3f88-0794-4919-a485-60f45cfc83a5)

#### PoC 2 - SQLi to Read Data from PostgresDB 
1. Steps 1 and 2 are the same as PoC 1.
2. Modify the intercepted "/admin/?action=save-news" request to look like the SS below and send the request:
    2.1 - Set the "authorEmail" field in the body to "`test'/*@[email.com](http://email.com/)`".
    2.2 - Set the "linkTitle" field in the body to "`*/,1,1,1,1,1,1,1);SELECT+remember_me+FROM+faquser+limit+1+offset+1%3b--`".
![image (1)](https://github.com/thorsten/phpMyFAQ/assets/63487456/131a6b5f-cfbf-4d94-9851-73f4d9e1605a)

#### PoC 3 - SQLi to Read Files from PostgresDB 
1. Steps 1 and 2 are the same as PoC 1.
2. Modify the intercepted "/admin/?action=save-news" request to look like the SS below and send the request:
    2.1 - Set the "authorEmail" field in the body to "`test'/*@[email.com](http://email.com/)`".
    2.2 - Set the "linkTitle" field in the body to "`*/,1,1,1,1,1,(select+pg_read_file(CONCAT(CHR(67),CHR(58),CHR(92),CHR(87),CHR(105),CHR(110),CHR(100),CHR(111),CHR(119),CHR(115),CHR(92),CHR(119),CHR(105),CHR(110),CHR(46),CHR(105),CHR(110),CHR(105)))),1)--`". (_the CONCAT() and CHR() functions are used to bypass the escaping of single quotes, these characters in its decoded form is "select pg_read_file('C:\Windows\win.ini')"_)
![image (2)](https://github.com/thorsten/phpMyFAQ/assets/63487456/61857d4c-4eab-43e3-87fa-20eefe6553e5)

#### PoC 4 - SQLi to Shell
It is also possible to obtain a shell if superuser is enabled on the postgres DB. These are the high level steps of the exploit chain:

1. Create a table called "cmd_exec" to store the payload.
2. Create a function in postgres to store the command to write a web shell to the "../htdocs" directory. (This step is required as CONCAT() function cannot be used to bypass the step where; "COPY cmd_exec FROM PROGRAM '<command>' " is run as it requires single quotes.)
3. Trigger the function to write the PHP web shell at "`http://<URL>/shell.php`" that takes in commands via the "?cmd=" parameter.
4. Send the Python reverse shell command via a GET request to launch the reverse shell. 

The video demo and the Python PoC script can be accessed from this link: https://drive.google.com/drive/folders/1BFL8GHIBxSUxu0TneYf66KjFA0A4RZga?usp=sharing

### Impact
The SQL injection vulnerability discovered in the "Add News" functionality of the application allows authenticated users with appropriate privileges to execute malicious SQL queries, potentially leading to data exfiltration, account takeover, and even remote code execution. Attackers can exploit the vulnerability to read sensitive data from the database, such as user credentials and system files, compromising the confidentiality and integrity of the system. Moreover, successful exploitation may enable attackers to gain unauthorized access to user accounts or execute arbitrary commands on the server, impacting both system administrators and end users.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-qgxx-4xv5-6hcw
- https://nvd.nist.gov/vuln/detail/CVE-2024-27299
- https://github.com/thorsten/phpMyFAQ/commit/1b68a5f89fb65996c56285fa636b818de8608011
- https://drive.google.com/drive/folders/1BFL8GHIBxSUxu0TneYf66KjFA0A4RZga?usp=sharing
- https://github.com/thorsten/phpMyFAQ
