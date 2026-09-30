# [C] knowns before 0.31.0 External Control of Agent Working Directory via x-opencode-directory Header

## Summary
Severity: Critical
Advisory: CVE-2026-88899
Aliases: GHSA-9h2q-r9fh-f98w
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88899
Type: osv

## Details
knowns versions before 0.31.0 fail to properly validate the x-opencode-directory request header in the /api/opencode proxy endpoint. Remote attackers can supply arbitrary directory paths to execute file operations outside the project root on the host system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88899.json
- https://github.com/knowns-dev/knowns/releases/tag/v0.31.0
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-9h2q-r9fh-f98w
- https://nvd.nist.gov/vuln/detail/CVE-2026-88899
- https://www.vulncheck.com/advisories/knowns-before-0.31.0-external-control-of-agent-working-directory-via-x-opencode-directory-header
- https://github.com/knowns-dev/knowns/commit/37db0561b37b48b8bd035a417d7f1da6258ae657
- https://github.com/knowns-dev/knowns/blob/v0.30.0/internal/server/server.go#L1283-L1296
