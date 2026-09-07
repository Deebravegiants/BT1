# [C] Moodle blind Server-Side Request Forgery (SSRF) vulnerability in LTI provider library

## Summary
Severity: Critical
Advisory: GHSA-xqcf-vgqc-pcmg
CVE: CVE-2022-45152
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-11-25
Source: https://github.com/advisories/GHSA-xqcf-vgqc-pcmg
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.18
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.11
- Packagist: `moodle/moodle` — affected >=4.0 <4.0.5

## Details
A blind Server-Side Request Forgery (SSRF) vulnerability was found in Moodle. This flaw exists due to insufficient validation of user-supplied input in LTI provider library. The library does not utilise Moodle's inbuilt cURL helper, which resulted in a blind SSRF risk. An attacker can send a specially crafted HTTP request and trick the application to initiate requests to arbitrary systems. This vulnerability allows a remote attacker to perform SSRF attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45152
- https://bugzilla.redhat.com/show_bug.cgi?id=2142775
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2DHYIIAUXUBHMBEDYU7TYNZXEN2W2SA2
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/74SXNGA5RIWM7QNX7H3G7SYIQLP4UUGV
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NLRJB5JNKK3VVBLV3NH3RI7COEDAXSAB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2DHYIIAUXUBHMBEDYU7TYNZXEN2W2SA2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/74SXNGA5RIWM7QNX7H3G7SYIQLP4UUGV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NLRJB5JNKK3VVBLV3NH3RI7COEDAXSAB
- https://moodle.org/mod/forum/discuss.php?d=440772
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-71920
