# [H] Ollama downloadBlob Improper Validation of Array Index Denial-of-Service Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-15685
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-15685
Type: osv

## Details
Ollama downloadBlob Improper Validation of Array Index Denial-of-Service Vulnerability. This vulnerability allows remote attackers to create a denial-of-service condition on affected installations of Ollama. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the downloadBlob function. The issue results from the lack of proper validation of user-supplied data, which can result in a memory access past the end of an allocated array. An attacker can leverage this vulnerability to create a denial-of-service condition on the system. Was ZDI-CAN-27277.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15685.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15685
- https://www.zerodayinitiative.com/advisories/ZDI-26-403/
