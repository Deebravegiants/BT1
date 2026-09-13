# [C] Renovate 37.158.0 before 37.199.0 Command Injection via helmv3

## Summary
Severity: Critical
Advisory: CVE-2024-58376
Aliases: GHSA-rqgv-292v-5qgr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2024-58376
Type: osv

## Details
Renovate versions 37.158.0 before 37.199.0 contain a command injection vulnerability in the helmv3 manager's registryAliases handling that allows attackers with commit access to execute arbitrary commands. Attackers can manipulate registryAliases keys with unquoted shell metacharacters to inject commands executed during helm repo add operations, gaining full access to Renovate's execution environment.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58376.json
- https://github.com/renovatebot/renovate/security/advisories/GHSA-rqgv-292v-5qgr
- https://nvd.nist.gov/vuln/detail/CVE-2024-58376
- https://www.vulncheck.com/advisories/renovate-before-command-injection-via-helmv3
