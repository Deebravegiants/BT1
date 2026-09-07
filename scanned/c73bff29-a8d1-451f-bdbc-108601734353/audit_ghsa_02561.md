# [H] Sensitive Data Exposure in miniorange_saml

## Summary
Severity: High
Advisory: GHSA-g485-29gq-6h2h
CVE: CVE-2021-36786
CWE: CWE-922
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-g485-29gq-6h2h
Type: github-advisory

## Affected
- Packagist: `miniorange/miniorange-saml` — affected >=0 <1.4.3

## Details
The miniorange_saml (aka Miniorange Saml) extension before 1.4.3 for TYPO3 allows Sensitive Data Exposure of API credentials and private keys.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36786
- https://github.com/miniOrangeDev/miniorange-saml-typo3-sso
- https://typo3.org/security/advisory/typo3-ext-sa-2021-011
