# [H] CVE-2021-43289

## Summary
Severity: High
Advisory: CVE-2021-43289
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2021-43289
Type: osv

## Details
An issue was discovered in ThoughtWorks GoCD before 21.3.0. An attacker who has compromised a GoCD agent can upload a malicious file into an arbitrary directory of a GoCD server, but does not control the filename.

## References
- https://www.gocd.org/releases/#21-3-0
- https://blog.sonarsource.com/gocd-vulnerability-chain
- https://github.com/gocd/gocd/commit/4c4bb4780eb0d3fc4cacfc4cfcc0b07e2eaf0595
- https://github.com/gocd/gocd/commit/c22e0428164af25d3e91baabd3f538a41cadc82f
