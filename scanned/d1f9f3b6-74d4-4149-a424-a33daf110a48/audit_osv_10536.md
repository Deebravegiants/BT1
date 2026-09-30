# [M] CVE-2017-16893

## Summary
Severity: Medium
Advisory: CVE-2017-16893
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-01
Source: https://osv.dev/vulnerability/CVE-2017-16893
Type: osv

## Details
The application Piwigo is affected by an SQL injection vulnerability in version 2.9.2 and possibly prior. This vulnerability allows remote authenticated attackers to obtain information in the context of the user used by the application to retrieve data from the database. tags.php is affected: values of the edit_list parameters are not sanitized; these are used to construct an SQL query and retrieve a list of registered users into the application.

## References
- https://github.com/Piwigo/Piwigo/issues/804
