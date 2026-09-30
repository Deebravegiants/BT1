# [M] Roundcube: Bypass of remote image blocking via crafted BODY background attribute

## Summary
Severity: Medium
Advisory: GHSA-5hf6-crg4-fg59
CVE: CVE-2026-35542
CWE: CWE-669
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-5hf6-crg4-fg59
Type: github-advisory

## Affected
- Packagist: `roundcube/roundcubemail` — affected >=1.7-beta <1.7-rc5

## Details
An issue was discovered in Roundcube Webmail before 1.5.14 and 1.6.14. The remote image blocking feature can be bypassed via a crafted background attribute of a BODY element in an e-mail message. This may lead to information disclosure or access-control bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35542
- https://github.com/roundcube/roundcubemail/commit/e052328e3dc75f13adc2e314eaa4096ac21084ad
- https://github.com/roundcube/roundcubemail/commit/fd0e98178db5c73eaa93d005b561874923f9b0f0
- https://github.com/roundcube/roundcubemail/commit/fde14d01adc9f37893cd82b635883e516ed453f8
- https://github.com/roundcube/roundcubemail
- https://github.com/roundcube/roundcubemail/releases/tag/1.5.14
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.14
- https://github.com/roundcube/roundcubemail/releases/tag/1.7-rc5
- https://roundcube.net/news/2026/03/18/security-updates-1.7-rc5-1.6.14-1.5.14
