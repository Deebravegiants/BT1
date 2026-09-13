# [C] Apache OpenMeetings has Inadequate Encryption Strength

## Summary
Severity: Critical
Advisory: GHSA-cqm6-hrgq-6869
CVE: CVE-2017-7673
CWE: CWE-326
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cqm6-hrgq-6869
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=1.0.0 <3.3.0

## Details
Apache OpenMeetings 1.0.0 uses not very strong cryptographic storage, captcha is not used in registration and forget password dialogs and auth forms missing brute force protection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7673
- https://github.com/apache/openmeetings
- http://markmail.org/message/3hshl26omwjo6c5i
- http://www.securityfocus.com/bid/99587
