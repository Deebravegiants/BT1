# [M] Cross-Site Request Forgery (CSRF) in automad/automad

## Summary
Severity: Medium
Advisory: GHSA-4j8w-p6hv-3qxc
CVE: CVE-2023-7038
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-4j8w-p6hv-3qxc
Type: github-advisory

## Affected
- Packagist: `automad/automad` — affected >=0 <2.0.0-alpha.1

## Details
automad up to 1.10.9 does not implement anti-CSRF tokens by default, making it vulnerable Cross-Site Request Forgery (CSRF). An attacker may exploit this vulnerability to force an admin into creating or deleting users. An exploit has been disclosed publicly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-7038
- https://github.com/marcantondahmen/automad
- https://github.com/screetsec/VDD/tree/main/Automad%20CMS/Cross-Site%20Request%20Forgery%20(CSRF)
- https://vuldb.com/?ctiid.248687
- https://vuldb.com/?id.248687
