# [C] CVE-2020-28020

## Summary
Severity: Critical
Advisory: CVE-2020-28020
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28020
Type: osv

## Details
Exim 4 before 4.92 allows Integer Overflow to Buffer Overflow, in which an unauthenticated remote attacker can execute arbitrary code by leveraging the mishandling of continuation lines during header-length restriction.

## References
- http://www.openwall.com/lists/oss-security/2021/07/25/1
- http://www.openwall.com/lists/oss-security/2021/08/03/1
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28020-HSIZE.txt
