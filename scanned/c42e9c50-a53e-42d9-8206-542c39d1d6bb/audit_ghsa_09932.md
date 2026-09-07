# [M] Nodcms contains a cross-site request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3qcm-pj6q-w4c5
CVE: CVE-2016-20054
CWE: CWE-352, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-3qcm-pj6q-w4c5
Type: github-advisory

## Affected
- Packagist: `khodakhah/nodcms` — affected >=0

## Details
Nodcms contains a cross-site request forgery vulnerability that allows attackers to perform unauthorized administrative actions by crafting malicious forms. Attackers can trick authenticated administrators into submitting requests to admin/user_manipulate and admin/settings/generall endpoints to create users or modify application settings without explicit consent.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-20054
- https://github.com/khodakhah/nodcms
- https://www.exploit-db.com/exploits/40707
