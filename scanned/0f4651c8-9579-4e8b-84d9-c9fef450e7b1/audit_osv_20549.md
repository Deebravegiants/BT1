# [H] CVE-2021-34992

## Summary
Severity: High
Advisory: CVE-2021-34992
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-15
Source: https://osv.dev/vulnerability/CVE-2021-34992
Type: osv

## Details
This vulnerability allows remote attackers to execute arbitrary code on affected installations of Orckestra C1 CMS 6.10. Authentication is required to exploit this vulnerability. The specific flaw exists within Composite.dll. The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of the service account. Was ZDI-CAN-14740.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-21-1304/
- https://github.com/Orckestra/C1-CMS-Foundation/releases/tag/v6.11
