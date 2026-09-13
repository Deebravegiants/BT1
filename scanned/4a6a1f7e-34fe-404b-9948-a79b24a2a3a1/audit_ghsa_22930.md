# [H] OXID eShop user impersonation vulnerability

## Summary
Severity: High
Advisory: GHSA-4c39-hj99-5h2r
CVE: CVE-2015-6926
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4c39-hj99-5h2r
Type: github-advisory

## Affected
- Packagist: `oxid-esales/oxideshop-ce` — affected >=0 <4.5.0

## Details
The OpenID Single Sign-On authentication functionality in OXID eShop before 4.5.0 allows remote attackers to impersonate users via the email address in a crafted authentication token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-6926
- https://bugs.oxid-esales.com/view.php?id=6224
- https://github.com/OXID-eSales/oxideshop_ce
- https://oxidforge.org/en/oxid-security-bulletin-2015-001.html
