# [M] Moderate severity vulnerability that affects org.b3log:symphony

## Summary
Severity: Medium
Advisory: GHSA-xgjc-49cw-529m
CVE: CVE-2019-9142
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-03-06
Source: https://github.com/advisories/GHSA-xgjc-49cw-529m
Type: github-advisory

## Affected
- Maven: `org.b3log:symphony` — affected >=0 <3.4.7

## Details
An issue was discovered in b3log Symphony (aka Sym) before v3.4.7. XSS exists via the userIntro and userNickname fields to processor/SettingsProcessor.java.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9142
- https://github.com/b3log/symphony/issues/860
- https://github.com/advisories/GHSA-xgjc-49cw-529m
- https://github.com/b3log/symphony
