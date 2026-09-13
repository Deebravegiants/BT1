# [H] CVE-2018-6533

## Summary
Severity: High
Advisory: CVE-2018-6533
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-27
Source: https://osv.dev/vulnerability/CVE-2018-6533
Type: osv

## Details
An issue was discovered in Icinga 2.x through 2.8.1. By editing the init.conf file, Icinga 2 can be run as root. Following this the program can be used to run arbitrary code as root. This was fixed by no longer using init.conf to determine account information for any root-executed code (a larger issue than CVE-2017-16933).

## References
- https://github.com/Icinga/icinga2/pull/5850
