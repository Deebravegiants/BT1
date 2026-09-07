# [M] Moodle Stored XSS and blind SSRF possible via SCORM track details

## Summary
Severity: Medium
Advisory: GHSA-wwv7-h477-wrv7
CVE: CVE-2022-35651
CWE: CWE-79, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-wwv7-h477-wrv7
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.15
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.8
- Packagist: `moodle/moodle` — affected >=4.0 <4.0.2

## Details
A stored Cross-site Scripting (XSS) and blind Server-Side Request Forgery (SSRF) vulnerability was found in Moodle, occurs due to insufficient sanitization of user-supplied data in the SCORM track details. A remote attacker can trick the victim to follow a specially crafted link and execute arbitrary HTML and script code in user's browser in context of vulnerable website to steal potentially sensitive information, change appearance of the web page, can perform phishing and drive-by-download attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35651
- https://bugzilla.redhat.com/show_bug.cgi?id=2106275
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6MOKYVRNFNAODP2XSMGJ5CRDUZCZKAR3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MTKUSFPSYFINSQFSOHDQIDVE6FWBEU6V
- https://moodle.org/mod/forum/discuss.php?d=436458
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-71921
