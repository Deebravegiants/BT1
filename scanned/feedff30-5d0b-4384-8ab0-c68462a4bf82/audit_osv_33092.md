# [H] Cloudera Hue Ace Editor Directory Traversal Information Disclosure Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-3884
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-05-22
Source: https://osv.dev/vulnerability/CVE-2025-3884
Type: osv

## Details
Cloudera Hue Ace Editor Directory Traversal Information Disclosure Vulnerability. This vulnerability allows remote attackers to disclose sensitive information on affected installations of Cloudera Hue. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the Ace Editor web application. The issue results from the lack of proper validation of a user-supplied path prior to using it in file operations. An attacker can leverage this vulnerability to disclose information in the context of the service account. Was ZDI-CAN-24332.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/3xxx/CVE-2025-3884.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-3884
- https://www.zerodayinitiative.com/advisories/ZDI-25-250/
