# [H] REDAXO CMS is vulnerable to RCE attack through its template management component

## Summary
Severity: High
Advisory: GHSA-xj9j-gjxg-7jvq
CVE: CVE-2025-64050
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-xj9j-gjxg-7jvq
Type: github-advisory

## Affected
- Packagist: `redaxo/source` — affected >=0 <5.20.1

## Details
A Remote Code Execution (RCE) vulnerability in the template management component in REDAXO CMS 5.20.0 allows remote authenticated administrators to execute arbitrary operating system commands by injecting PHP code into an active template. The payload is executed when visitors access frontend pages using the compromised template.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64050
- https://github.com/redaxo/redaxo/pull/6372/commits/bc96462e20f7e651b2e6c3bb59d141d5cb09af0f
- https://drive.google.com/drive/folders/1Via4r4wn5zCcBllWmHpxYweCPgcbN0bz?usp=sharing
- https://github.com/redaxo/redaxo
- https://github.com/vettrivel007/CVE-Disclosures/blob/main/CVE-2025-64050.md
