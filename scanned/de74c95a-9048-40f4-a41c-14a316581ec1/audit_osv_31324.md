# [H] BlueZ HID over GATT Profile Improper Access Control Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2024-8805
CVSS: 8.8 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-22
Source: https://osv.dev/vulnerability/CVE-2024-8805
Type: osv

## Details
BlueZ HID over GATT Profile Improper Access Control Remote Code Execution Vulnerability. This vulnerability allows network-adjacent attackers to execute arbitrary code on affected installations of BlueZ. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the implementation of the HID over GATT Profile. The issue results from the lack of authorization prior to allowing access to functionality. An attacker can leverage this vulnerability to execute code in the context of the current user. Was ZDI-CAN-25177.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8805.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8805
- https://www.zerodayinitiative.com/advisories/ZDI-24-1229/
