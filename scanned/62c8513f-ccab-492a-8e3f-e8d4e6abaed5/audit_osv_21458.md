# [H] CVE-2021-43286

## Summary
Severity: High
Advisory: CVE-2021-43286
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2021-43286
Type: osv

## Details
An issue was discovered in ThoughtWorks GoCD before 21.3.0. An attacker with privileges to create a new pipeline on a GoCD server can abuse a command-line injection in the Git URL "Test Connection" feature to execute arbitrary code.

## References
- https://www.gocd.org/releases/#21-3-0
- https://blog.sonarsource.com/gocd-vulnerability-chain
- https://github.com/gocd/gocd/commit/2b77b533abcbb79c8fc758dec9984305dc1ade42
- https://github.com/gocd/gocd/commit/6fa9fb7a7c91e760f1adc2593acdd50f2d78676b
