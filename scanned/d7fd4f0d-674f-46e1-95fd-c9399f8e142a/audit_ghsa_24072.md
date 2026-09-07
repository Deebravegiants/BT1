# [H] Mautic Cross-Site Request Forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-7vvh-xqq4-w777
CVE: CVE-2017-8874
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7vvh-xqq4-w777
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected 1.4.1

## Details
Multiple cross-site request forgery (CSRF) vulnerabilities in Mautic 1.4.1 allow remote attackers to hijack the authentication of users for requests that (1) delete email campaigns or (2) delete contacts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8874
- https://github.com/mautic/mautic/issues/3486
- https://github.com/mautic/mautic
