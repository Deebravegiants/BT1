# [H] CVE-2020-12847

## Summary
Severity: High
Advisory: CVE-2020-12847
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-04
Source: https://osv.dev/vulnerability/CVE-2020-12847
Type: osv

## Details
Pydio Cells 2.0.4 web application offers an administrative console named “Cells Console” that is available to users with an administrator role. This console provides an administrator user with the possibility of changing several settings, including the application’s mailer configuration. It is possible to configure a few engines to be used by the mailer application to send emails. If the user selects the “sendmail” option as the default one, the web application offers to edit the full path where the sendmail binary is hosted. Since there is no restriction in place while editing this value, an attacker authenticated as an administrator user could force the web application into executing any arbitrary binary.

## References
- http://packetstormsecurity.com/files/158002/Pydio-Cells-2.0.4-XSS-File-Write-Code-Execution.html
- https://www.coresecurity.com/advisories
- https://www.coresecurity.com/core-labs/advisories/pydio-cells-204-multiple-vulnerabilities
