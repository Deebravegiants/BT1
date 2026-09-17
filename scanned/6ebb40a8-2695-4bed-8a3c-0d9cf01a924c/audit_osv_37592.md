# [M] OpenClaw < 2026.2.22 - Allowlist Parsing Mismatch in system.run Shell Chains

## Summary
Severity: Medium
Advisory: CVE-2026-31993
Aliases: GHSA-5f9p-f3w2-fwch
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:A/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-31993
Type: osv

## Details
OpenClaw versions prior to 2026.2.22 contain an allowlist parsing mismatch vulnerability in the macOS companion app that allows authenticated operators to bypass exec approval checks. Attackers with operator.write privileges and a paired macOS beta node can craft shell-chain payloads that pass incomplete allowlist validation and execute arbitrary commands on the paired host.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31993.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5f9p-f3w2-fwch
- https://nvd.nist.gov/vuln/detail/CVE-2026-31993
- https://www.vulncheck.com/advisories/openclaw-allowlist-parsing-mismatch-in-system-run-shell-chains
- https://github.com/openclaw/openclaw/commit/5da03e622119fa012285cdb590fcf4264c965cb5
- https://github.com/openclaw/openclaw/commit/e371da38aab99521c4e076cd3d95fd775e00b784
