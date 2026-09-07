# [M] phpCAS client library and Moodle Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-45ch-hxgr-vx8j
CVE: CVE-2010-1618
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-45ch-hxgr-vx8j
Type: github-advisory

## Affected
- Packagist: `apereo/phpcas` — affected >=0 <1.1.0
- Packagist: `moodle/moodle` — affected >=1.8.0 <1.8.12
- Packagist: `moodle/moodle` — affected >=1.9.0 <1.9.8

## Details
Cross-site scripting (XSS) vulnerability in the phpCAS client library before 1.1.0, as used in Moodle 1.8.x before 1.8.12 and 1.9.x before 1.9.8, allows remote attackers to inject arbitrary web script or HTML via a crafted URL, which is not properly handled in an error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1618
- https://github.com/apereo/phpCAS/commit/021633112198b37555b35340cde884d1016d9e47
- https://github.com/apereo/phpCAS
- http://lists.opensuse.org/opensuse-security-announce/2010-05/msg00001.html
- http://moodle.org/security
- http://www.ja-sig.org/issues/browse/PHPCAS-52
- http://www.ja-sig.org/wiki/display/CASC/phpCAS+ChangeLog
- http://www.vupen.com/english/advisories/2010/1107
