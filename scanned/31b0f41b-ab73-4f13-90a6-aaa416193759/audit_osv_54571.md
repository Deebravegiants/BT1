# [M] CVE-2024-11612

## Summary
Severity: Medium
Advisory: CVE-2024-11612
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-11-22
Source: https://osv.dev/vulnerability/CVE-2024-11612
Type: osv

## Details
7-Zip CopyCoder Infinite Loop Denial-of-Service Vulnerability. This vulnerability allows remote attackers to create a denial-of-service condition on affected installations of 7-Zip. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the processing of streams. The issue results from a logic error that can lead to an infinite loop. An attacker can leverage this vulnerability to create a denial-of-service condition on the system. Was ZDI-CAN-24307.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-24-1606/
