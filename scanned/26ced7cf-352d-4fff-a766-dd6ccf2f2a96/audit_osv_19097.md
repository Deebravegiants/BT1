# [C] CVE-2020-7378

## Summary
Severity: Critical
Advisory: CVE-2020-7378
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-11-24
Source: https://osv.dev/vulnerability/CVE-2020-7378
Type: osv

## Details
CRIXP OpenCRX version 4.30 and 5.0-20200717 and prior suffers from an unverified password change vulnerability. An attacker who is able to connect to the affected OpenCRX instance can change the password of any user, including admin-Standard, to any chosen value. This issue was resolved in version 5.0-20200904, released September 4, 2020.

## References
- https://blog.rapid7.com/2020/11/24/cve-2020-7378-opencrx-unverified-password-change/
