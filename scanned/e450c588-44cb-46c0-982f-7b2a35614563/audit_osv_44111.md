# [M] Nuclio: Unauthenticated OS command injection via namespace header in list-all resource path on local platform

## Summary
Severity: Medium
Advisory: CVE-2026-79756
Aliases: GHSA-mq8w-f7w8-5rgg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-79756
Type: osv

## Details
Nuclio is a "Serverless" framework for Real-Time Events and Data Processing. Prior to version 1.17.4, the fix for unauthenticated OS command injection in the nuclio dashboard on the local/Docker platform is incomplete. The fix added validateFunctionName for function names and common.Quote() for the named-resource shell command path, but the list-all resource path (triggered when no specific resource name is provided) still interpolates the resourceNamespace parameter unquoted into a /bin/sh -c command string. An unauthenticated attacker can inject shell metacharacters via the X-Nuclio-Function-Namespace, X-Nuclio-Project-Namespace, or X-Nuclio-Function-Event-Namespace HTTP headers to achieve arbitrary command execution inside the dashboard container. This issue has been patched in version 1.17.4.

## References
- https://github.com/nuclio/nuclio/releases/tag/1.17.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79756.json
- https://github.com/nuclio/nuclio/security/advisories/GHSA-mq8w-f7w8-5rgg
- https://nvd.nist.gov/vuln/detail/CVE-2026-79756
- https://github.com/nuclio/nuclio/commit/86d4e39387d8845f567649201798800830f08411
- https://github.com/nuclio/nuclio/pull/4223
