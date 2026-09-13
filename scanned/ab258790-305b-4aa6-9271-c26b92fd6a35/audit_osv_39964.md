# [H] Warp may allow terminal output to access the local clipboard through OSC 52

## Summary
Severity: High
Advisory: CVE-2026-48725
Aliases: GHSA-wgqj-4c26-7c4g
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-48725
Type: osv

## Details
Warp is an agentic development environment. From 0.2021.04.25.23.05.stable_00 until 0.2026.05.06.15.42.stable_01, Warp allows terminal output to request access to the local system clipboard. A malicious remote host, remote program, or other attacker-controlled terminal output source can trigger clipboard reads or writes without a separate confirmation step. This crosses the trust boundary between untrusted terminal output and the user's local desktop clipboard. This vulnerability is fixed in 0.2026.05.06.15.42.stable_01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48725.json
- https://github.com/warpdotdev/warp/security/advisories/GHSA-wgqj-4c26-7c4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-48725
- https://github.com/warpdotdev/warp/commit/b1a41d0b1aba9f40db1e5ceb695183452a894003
