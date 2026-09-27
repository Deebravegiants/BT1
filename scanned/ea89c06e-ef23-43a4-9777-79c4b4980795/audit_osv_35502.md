# [M] Open WebUI Cleartext Transmission of Credentials Information Disclosure Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-0767
CVSS: 5.3 (CVSS:3.0/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-0767
Type: osv

## Details
Open WebUI Cleartext Transmission of Credentials Information Disclosure Vulnerability. This vulnerability allows network-adjacent attackers to disclose sensitive information on affected installations of Open WebUI. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the handling of credentials provided to the endpoint. The issue results from transmitting sensitive information in plaintext. An attacker can leverage this vulnerability to disclose transmitted credentials, leading to further compromise. Was ZDI-CAN-28259.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0767.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0767
- https://www.zerodayinitiative.com/advisories/ZDI-26-033/
