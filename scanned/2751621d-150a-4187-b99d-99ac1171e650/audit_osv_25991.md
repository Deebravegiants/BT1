# [M] Symbolicator Server Side Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-49094
Aliases: GHSA-6576-pr6j-h9c6
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-11-30
Source: https://osv.dev/vulnerability/CVE-2023-49094
Type: osv

## Details
Symbolicator is a symbolication service for native stacktraces and minidumps with symbol server support. An attacker could make Symbolicator send arbitrary GET HTTP requests to internal IP addresses by using a specially crafted HTTP endpoint. The response could be reflected to the attacker if they have an account on Sentry instance. The issue has been fixed in the release 23.11.2.

## References
- https://github.com/getsentry/symbolicator/releases/tag/23.11.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49094.json
- https://github.com/getsentry/symbolicator/security/advisories/GHSA-6576-pr6j-h9c6
- https://nvd.nist.gov/vuln/detail/CVE-2023-49094
- https://github.com/getsentry/symbolicator/commit/9db2fb9197dd200d62aacebd8efef4df7678865a
- https://github.com/getsentry/symbolicator/pull/1332
