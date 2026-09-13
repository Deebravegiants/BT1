# [C] Renovate before 44.14.7 Command Injection via Mix organization

## Summary
Severity: Critical
Advisory: CVE-2026-88888
Aliases: GHSA-v85g-rq5w-c46q
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88888
Type: osv

## Details
Renovate before 44.14.7 contains a command injection vulnerability in the Mix manager when processing private dependencies with unescaped organization parameters. Attackers can inject shell metacharacters through malicious package names to execute arbitrary commands as the Renovate user in binarySource=docker mode.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88888.json
- https://github.com/renovatebot/renovate/security/advisories/GHSA-v85g-rq5w-c46q
- https://nvd.nist.gov/vuln/detail/CVE-2026-88888
- https://www.vulncheck.com/advisories/renovate-before-44.14.7-command-injection-via-mix-organization
