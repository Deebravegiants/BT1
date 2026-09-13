# [H] Warp: SSH remote output can lead to local file overwrite and persistence

## Summary
Severity: High
Advisory: CVE-2026-48720
Aliases: GHSA-5h96-jrrq-6hxq
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-48720
Type: osv

## Details
Warp is an agentic development environment. From 0.2025.03.05.08.02.stable_00 until 0.2026.05.06.15.42.stable_01, Warp accepts non-inline `OSC 1337;File` payloads from terminal output and materialize the decoded payload as a local file without an additional confirmation step. This vulnerability is fixed in 0.2026.05.06.15.42.stable_01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48720.json
- https://github.com/warpdotdev/warp/security/advisories/GHSA-5h96-jrrq-6hxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-48720
- https://github.com/warpdotdev/warp/commit/f3b9ce1c8fd13d037526c447418d809087722daa
