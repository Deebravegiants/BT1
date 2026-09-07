# [M] Mattermost Server does not neutralize HTML content in an Email template field

## Summary
Severity: Medium
Advisory: GHSA-wj5w-qghh-gvqp
CVE: CVE-2017-18892
CWE: CWE-116
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wj5w-qghh-gvqp
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.0.5
- Go: `github.com/mattermost/mattermost-server` — affected >=4.1.0 <4.1.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.0

## Details
An issue was discovered in Mattermost Server before 4.2.0, 4.1.1, and 4.0.5. E-mail templates can have a field in which HTML content is not neutralized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18892
- https://github.com/mattermost/mattermost/commit/4e05fbffed4d7ad75c0bb55d67d2c6f7cf9eaad6
- https://github.com/mattermost/mattermost/commit/d76946bdb545aba4088943fc523dabb459d22873
- https://github.com/mattermost/mattermost/commit/f5167f3ba645b829f4c28530e13be6c3db967255
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
