# [M] CVE-2024-7537

## Summary
Severity: Medium
Advisory: CVE-2024-7537
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-08-06
Source: https://osv.dev/vulnerability/CVE-2024-7537
Type: osv

## Details
oFono QMI SMS Handling Out-Of-Bounds Read Information Disclosure Vulnerability. This vulnerability allows local attackers to disclose sensitive information on affected installations of oFono. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the processing of SMS message lists. The issue results from the lack of proper validation of user-supplied data, which can result in a read past the end of an allocated buffer. An attacker can leverage this in conjunction with other vulnerabilities to execute arbitrary code in the context of root. Was ZDI-CAN-23157.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-24-1077/
