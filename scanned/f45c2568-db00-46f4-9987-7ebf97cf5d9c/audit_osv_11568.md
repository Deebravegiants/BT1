# [C] CVE-2017-8799

## Summary
Severity: Critical
Advisory: CVE-2017-8799
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-05
Source: https://osv.dev/vulnerability/CVE-2017-8799
Type: osv

## Details
Untrusted input execution via igetwild in all iRODS versions before 4.1.11 and 4.2.1 allows other iRODS users (potentially anonymous) to execute remote shell commands via iRODS virtual pathnames. To exploit this vulnerability, a virtual iRODS pathname that includes a semicolon would be retrieved via igetwild. Because igetwild is a Bash script, the part of the pathname following the semicolon would be executed in the user's shell.

## References
- https://github.com/irods/irods/issues/3452
