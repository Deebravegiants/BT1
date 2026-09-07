# [M] Moodle LTI module reflected XSS risk

## Summary
Severity: Medium
Advisory: GHSA-62wh-m4jr-233r
CVE: CVE-2022-35653
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-62wh-m4jr-233r
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.0 <4.0.2
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.8
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.15

## Details
A reflected XSS issue was identified in the LTI module of Moodle. The vulnerability exists due to insufficient sanitization of user-supplied data in the LTI module. A remote attacker can trick the victim to follow a specially crafted link and execute arbitrary HTML and script code in user's browser in context of vulnerable website to steal potentially sensitive information, change appearance of the web page, can perform phishing and drive-by-download attacks. This vulnerability does not impact authenticated users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35653
- https://bugzilla.redhat.com/show_bug.cgi?id=2106277
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6MOKYVRNFNAODP2XSMGJ5CRDUZCZKAR3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MTKUSFPSYFINSQFSOHDQIDVE6FWBEU6V
- https://moodle.org/mod/forum/discuss.php?d=436460
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-72299
