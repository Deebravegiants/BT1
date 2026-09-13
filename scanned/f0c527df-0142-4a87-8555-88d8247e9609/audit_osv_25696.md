# [C] Exim AUTH Out-Of-Bounds Write Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2023-42115
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-42115
Type: osv

## Details
Exim AUTH Out-Of-Bounds Write Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Exim. Authentication is not required to exploit this vulnerability. 

The specific flaw exists within the smtp service, which listens on TCP port 25 by default. The issue results from the lack of proper validation of user-supplied data, which can result in a write past the end of a buffer. An attacker can leverage this vulnerability to execute code in the context of the service account.
. Was ZDI-CAN-17434.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42115.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-42115
- https://www.zerodayinitiative.com/advisories/ZDI-23-1469/
