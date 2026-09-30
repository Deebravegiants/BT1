# [H] Netgate pfSense CE Suricata Path Traversal Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-12490
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-06
Source: https://osv.dev/vulnerability/CVE-2025-12490
Type: osv

## Details
Netgate pfSense CE Suricata Path Traversal Remote Code Execution Vulnerability. This vulnerability allows remote attackers to create arbitrary files on affected installations of Netgate pfSense. Authentication is required to exploit this vulnerability.

The specific flaw exists within the Suricata package. The issue results from the lack of proper validation of a user-supplied path prior to using it in file operations. An attacker can leverage this vulnerability to create files in the context of root. Was ZDI-CAN-28085.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12490.json
- https://github.com/pfsense/FreeBSD-ports/commit/36b2303dfca35a1183d76f26bcc6ce26d4ea682d
- https://nvd.nist.gov/vuln/detail/CVE-2025-12490
- https://www.zerodayinitiative.com/advisories/ZDI-25-979/
