# [M] Stored XSS in REDAXO

## Summary
Severity: Medium
Advisory: GHSA-7wj8-856p-qc9m
CVE: CVE-2024-13209
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-02-10
Source: https://github.com/advisories/GHSA-7wj8-856p-qc9m
Type: github-advisory

## Affected
- Packagist: `redaxo/source` — affected >=5.12.0-beta1 <5.18.2

## Details
### Summary
Stored XSS in REDAXO 5.18.1 - Article / "content/edit".

### Details
On the latest version of Redaxo, v5.18.1, the article name field is susceptible to stored XSS.

### Impact
A malicious actor can easily steal cookie using this stored XSS and perform a session hijacking attack.

## References
- https://github.com/redaxo/redaxo/security/advisories/GHSA-7wj8-856p-qc9m
- https://nvd.nist.gov/vuln/detail/CVE-2024-13209
- https://github.com/redaxo/redaxo/commit/74d7391571a29a455a0c477973bc25d25710e424
- https://geochen.medium.com/redaxo-cms-5-18-1-cross-site-scripting-7c9a872c72f6
- https://github.com/redaxo/redaxo
