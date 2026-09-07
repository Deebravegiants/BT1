# [M] Moodle stored-XSS vulnerability in some "social" user profile fields

## Summary
Severity: Medium
Advisory: GHSA-xv72-6pgh-cjj8
CVE: CVE-2022-45151
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-23
Source: https://github.com/advisories/GHSA-xv72-6pgh-cjj8
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.11
- Packagist: `moodle/moodle` — affected >=4.0 <4.0.5

## Details
The stored-XSS vulnerability was discovered in Moodle which exists due to insufficient sanitization of user-supplied data in several "social" user profile fields. An attacker could inject and execute arbitrary HTML and script code in user's browser in context of vulnerable website.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45151
- https://bugzilla.redhat.com/show_bug.cgi?id=2142774
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2DHYIIAUXUBHMBEDYU7TYNZXEN2W2SA2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/74SXNGA5RIWM7QNX7H3G7SYIQLP4UUGV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NLRJB5JNKK3VVBLV3NH3RI7COEDAXSAB
- https://moodle.org/mod/forum/discuss.php?d=440771
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-76131
