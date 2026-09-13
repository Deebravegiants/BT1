# [H] SEOmatic plugin for Craft CMS SSTI Vulnerability

## Summary
Severity: High
Advisory: GHSA-6j9m-rp7m-3gfg
CVE: CVE-2018-14716
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6j9m-rp7m-3gfg
Type: github-advisory

## Affected
- Packagist: `nystudio107/craft-seomatic` — affected >=0 <3.1.4

## Details
A Server Side Template Injection (SSTI) was discovered in the SEOmatic plugin before 3.1.4 for Craft CMS, because requests that don't match any elements incorrectly generate the canonicalUrl, and can lead to execution of Twig code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14716
- https://github.com/nystudio107/craft-seomatic/commit/1e7d1d084ac3a89e7ec70620f2749110508d1ce1
- https://github.com/nystudio107/craft-seomatic
- https://github.com/nystudio107/craft-seomatic/releases/tag/3.1.4
- https://twitter.com/nystudio107/status/1021847835418009605
- https://twitter.com/nystudio107/status/1021855169515057152
- https://www.exploit-db.com/exploits/45108
- http://ha.cker.info/exploitation-of-server-side-template-injection-with-craft-cms-plguin-seomatic
