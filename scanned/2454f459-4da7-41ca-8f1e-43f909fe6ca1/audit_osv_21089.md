# [C] CVE-2021-40543

## Summary
Severity: Critical
Advisory: CVE-2021-40543
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-11
Source: https://osv.dev/vulnerability/CVE-2021-40543
Type: osv

## Details
Opensis-Classic Version 8.0 is affected by a SQL injection vulnerability due to a lack of sanitization of input data at two parameters $_GET['usrid'] and $_GET['prof_id'] in the PasswordCheck.php file.

## References
- https://github.com/OS4ED/openSIS-Classic/issues/191
