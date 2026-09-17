# [C] CVE-2018-8712

## Summary
Severity: Critical
Advisory: CVE-2018-8712
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-14
Source: https://osv.dev/vulnerability/CVE-2018-8712
Type: osv

## Details
An issue was discovered in Webmin 1.840 and 1.880 when the default Yes setting of "Can view any file as a log file" is enabled. As a result of weak default configuration settings, limited users have full access rights to the underlying Unix system files, allowing the user to read sensitive data from the local system (using Local File Include) such as the '/etc/shadow' file via a "GET /syslog/save_log.cgi?view=1&file=/etc/shadow" request.

## References
- https://www.7elements.co.uk/resources/technical-advisories/webmin-1-840-1-880-unrestricted-access-arbitrary-files-using-local-file-include/
