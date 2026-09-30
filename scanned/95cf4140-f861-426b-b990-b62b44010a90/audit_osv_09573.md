# [C] CVE-2017-1000192

## Summary
Severity: Critical
Advisory: CVE-2017-1000192
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-17
Source: https://osv.dev/vulnerability/CVE-2017-1000192
Type: osv

## Details
Cygnux sysPass version 2.1.7 and older is vulnerable to a Local File Inclusion in the functionality of javascript files inclusion. The attacker can read the configuration files that contain the login and password from the database, private encryption key, as well as other sensitive information.

## References
- https://github.com/nuxsmin/sysPass/releases/tag/2.1.8.17042901
