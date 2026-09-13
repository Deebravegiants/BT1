# [C] CVE-2021-41280

## Summary
Severity: Critical
Advisory: CVE-2021-41280
Aliases: GHSA-hjjc-p9hr-424c
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-19
Source: https://osv.dev/vulnerability/CVE-2021-41280
Type: osv

## Details
Sharetribe Go is a source available marketplace software. In affected versions operating system command injection is possible on installations of Sharetribe Go, that do not have a secret AWS Simple Notification Service (SNS) notification token configured via the `sns_notification_token` configuration parameter. This configuration parameter is unset by default. The vulnerability has been patched in version 10.2.1. Users who are unable to upgrade should set the`sns_notification_token` configuration parameter to a secret value.

## References
- https://github.com/sharetribe/sharetribe/releases/tag/v10.2.1
- https://github.com/sharetribe/sharetribe/security/advisories/GHSA-hjjc-p9hr-424c
- https://github.com/sharetribe/sharetribe/commit/5b844f8108c5458d89f0d7ba974f42d7917b5f80
