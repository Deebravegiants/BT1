# [C] Pagekit CMS is vulnerable to OS Command Injection via Storage component

## Summary
Severity: Critical
Advisory: GHSA-m4f2-xpfq-h97v
CVE: CVE-2025-67164
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-17
Source: https://github.com/advisories/GHSA-m4f2-xpfq-h97v
Type: github-advisory

## Affected
- Packagist: `pagekit/pagekit` — affected >=0

## Details
An authenticated arbitrary file upload vulnerability in the /storage/poc.php component of Pagekit CMS v1.0.18 allows attackers to execute arbitrary code via uploading a crafted PHP file.

The project is archived as of December 1, 2023.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67164
- https://github.com/mbiesiad/vulnerability-research/tree/main/CVE-2025-67164
- https://github.com/pagekit/pagekit
