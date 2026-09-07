# [M] Moodle reflected cross-site scripting vulnerability in policy tool

## Summary
Severity: Medium
Advisory: GHSA-6gx2-g773-hv9h
CVE: CVE-2022-45150
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-23
Source: https://github.com/advisories/GHSA-6gx2-g773-hv9h
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.18
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.11
- Packagist: `moodle/moodle` — affected >=4.0 <4.0.5

## Details
A reflected cross-site scripting vulnerability was discovered in Moodle. This flaw exists due to insufficient sanitization of user-supplied data in policy tool. An attacker can trick the victim to open a specially crafted link that executes an arbitrary HTML and script code in user's browser in context of vulnerable website. This vulnerability may allow an attacker to perform cross-site scripting (XSS) attacks to gain access potentially sensitive information and modification of web pages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45150
- https://bugzilla.redhat.com/show_bug.cgi?id=2142773
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2DHYIIAUXUBHMBEDYU7TYNZXEN2W2SA2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/74SXNGA5RIWM7QNX7H3G7SYIQLP4UUGV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NLRJB5JNKK3VVBLV3NH3RI7COEDAXSAB
- https://moodle.org/mod/forum/discuss.php?d=440770
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-76091
