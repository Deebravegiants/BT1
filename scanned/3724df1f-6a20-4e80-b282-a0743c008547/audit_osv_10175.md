# [M] CVE-2017-14159

## Summary
Severity: Medium
Advisory: CVE-2017-14159
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/CVE-2017-14159
Type: osv

## Details
slapd in OpenLDAP 2.4.45 and earlier creates a PID file after dropping privileges to a non-root account, which might allow local users to kill arbitrary processes by leveraging access to this non-root account for PID file modification before a root script executes a "kill `cat /pathname`" command, as demonstrated by openldap-initscript.

## References
- http://www.openldap.org/its/index.cgi?findid=8703
- https://www.oracle.com/security-alerts/cpuapr2022.html
