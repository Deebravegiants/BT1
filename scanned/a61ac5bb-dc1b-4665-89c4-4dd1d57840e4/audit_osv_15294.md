# [C] CVE-2019-15052

## Summary
Severity: Critical
Advisory: CVE-2019-15052
Aliases: GHSA-4cwg-f7qc-6r95
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-14
Source: https://osv.dev/vulnerability/CVE-2019-15052
Type: osv

## Details
The HTTP client in Gradle before 5.6 sends authentication credentials originally destined for the configured host. If that host returns a 30x redirect, Gradle also sends those credentials to all subsequent hosts that the request redirects to. This is similar to CVE-2018-1000007.

## References
- https://github.com/gradle/gradle/issues/10278
- https://github.com/gradle/gradle/pull/10176
- https://github.com/gradle/gradle/security/advisories/GHSA-4cwg-f7qc-6r95
