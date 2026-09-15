# [H] CVE-2019-3781

## Summary
Severity: High
Advisory: CVE-2019-3781
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-07
Source: https://osv.dev/vulnerability/CVE-2019-3781
Type: osv

## Details
Cloud Foundry CLI, versions prior to v6.43.0, improperly exposes passwords when verbose/trace/debugging is turned on. A local unauthenticated or remote authenticated malicious user with access to logs may gain part or all of a users password.

## References
- http://www.securityfocus.com/bid/107365
- https://www.cloudfoundry.org/blog/cve-2019-3781
