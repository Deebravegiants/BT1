# [M] Elefant CMS Multiple XSS Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-qjjq-rcq8-jw6j
CVE: CVE-2012-1296
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qjjq-rcq8-jw6j
Type: github-advisory

## Affected
- Packagist: `elefant/cms` — affected >=1.0 <1.0.2-Beta
- Packagist: `elefant/cms` — affected >=1.1 <1.1.5-Beta

## Details
Multiple cross-site scripting (XSS) vulnerabilities in `apps/admin/handlers/preview.php` in Elefant CMS 1.0.x before 1.0.2-Beta and 1.1.x before 1.1.5-Beta allow remote attackers to inject arbitrary web script or HTML via the (1) title or (2) body parameter to admin/preview.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1296
- https://github.com/jbroadway/elefant/commit/1e38b1d91d9f8bfb4a0cda8316fe763a6cdd31d0
- https://github.com/jbroadway/elefant/commit/4fc4e0a704f697e593be927a447ca12b2863ff85
- https://exchange.xforce.ibmcloud.com/vulnerabilities/73421
- https://github.com/jbroadway/elefant
- https://web.archive.org/web/20120306001248/http://www.elefantcms.com/forum/discussion/39/elefant-1.0.2-and-1.1.5-security-updates-released
- https://web.archive.org/web/20200229030623/http://www.securityfocus.com/bid/52143
