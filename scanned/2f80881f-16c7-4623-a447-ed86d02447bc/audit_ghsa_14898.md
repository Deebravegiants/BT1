# [M] Reflected Cross-Site Scripting (XSS) in Dolibarr

## Summary
Severity: Medium
Advisory: GHSA-hv2j-6654-x74q
CVE: CVE-2024-34051
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-06-03
Source: https://github.com/advisories/GHSA-hv2j-6654-x74q
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <19.0.2

## Details
A Reflected Cross-site scripting (XSS) vulnerability located in htdocs/compta/paiement/card.php of Dolibarr before 19.0.2 allows remote attackers to inject arbitrary web script or HTML via a crafted payload injected into the facid parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34051
- https://github.com/Dolibarr/dolibarr/commit/3a3ccc253b8eceddee84f158b2c262a4033b9402
- https://blog.smarttecs.com/posts/2024-004-cve-2024-34051
- https://github.com/Dolibarr/dolibarr
