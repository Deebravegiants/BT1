# [H] CVE-2021-43287

## Summary
Severity: High
Advisory: CVE-2021-43287
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2021-43287
Type: osv

## Details
An issue was discovered in ThoughtWorks GoCD before 21.3.0. The business continuity add-on, which is enabled by default, leaks all secrets known to the GoCD server to unauthenticated attackers.

## References
- https://www.gocd.org/releases/#21-3-0
- https://blog.sonarsource.com/gocd-pre-auth-pipeline-takeover
- https://github.com/gocd/gocd/commit/41abc210ac4e8cfa184483c9ff1c0cc04fb3511c
