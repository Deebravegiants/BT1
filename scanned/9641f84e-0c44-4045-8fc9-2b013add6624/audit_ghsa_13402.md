# [C] Code injection in wix-embedded-mysql

## Summary
Severity: Critical
Advisory: GHSA-fx3v-4w3w-wpwr
CVE: CVE-2023-39021
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-fx3v-4w3w-wpwr
Type: github-advisory

## Affected
- Maven: `com.wix:wix-embedded-mysql` — affected >=0

## Details
wix-embedded-mysql v4.6.2 and below was discovered to contain a code injection vulnerability in the component com.wix.mysql.distribution.Setup.apply. This vulnerability is exploited via passing an unchecked argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39021
- https://github.com/LetianYuan/My-CVE-Public-References/tree/main/com_wix_wix-embedded-mysql
- https://github.com/wix/wix-embedded-mysql
