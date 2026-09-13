# [M] CVE-2017-9463

## Summary
Severity: Medium
Advisory: CVE-2017-9463
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-06-14
Source: https://osv.dev/vulnerability/CVE-2017-9463
Type: osv

## Details
The application Piwigo is affected by a SQL injection vulnerability in version 2.9.0 and possibly prior. This vulnerability allows remote authenticated attackers to obtain information in the context of the user used by the application to retrieve data from the database. The user_list_backend.php component is affected: values of the iDisplayStart & iDisplayLength parameters are not sanitized; these are used to construct a SQL query and retrieve a list of registered users into the application.

## References
- https://www.wizlynxgroup.com/security-research-advisories/vuln/WLX-2017-003
- https://github.com/Piwigo/Piwigo/commit/42920897ce927c236728d387f61bf03d117109a2
- https://github.com/Piwigo/Piwigo/issues/705
