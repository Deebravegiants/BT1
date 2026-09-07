# [M] Moodle Session Fixation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j5rc-cr5w-vfg6
CVE: CVE-2010-1613
CWE: CWE-287, CWE-384
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j5rc-cr5w-vfg6
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=1.8.0 <1.9.8

## Details
Moodle 1.8.x and 1.9.x before 1.9.8 does not enable the "Regenerate session id during login" setting by default, which makes it easier for remote attackers to conduct session fixation attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1613
- https://github.com/moodle/moodle
- http://lists.opensuse.org/opensuse-security-announce/2010-05/msg00001.html
- http://moodle.org/security
