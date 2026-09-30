# [H] CVE-2016-10729

## Summary
Severity: High
Advisory: CVE-2016-10729
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-24
Source: https://osv.dev/vulnerability/CVE-2016-10729
Type: osv

## Details
An issue was discovered in Amanda 3.3.1. A user with backup privileges can trivially compromise a client installation. The "runtar" setuid root binary does not check for additional arguments supplied after --create, allowing users to manipulate commands and perform command injection as root.

## References
- https://www.exploit-db.com/exploits/39217/
