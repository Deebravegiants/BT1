# [H] Warp: OS command injection when opening terminal links from WSL

## Summary
Severity: High
Advisory: CVE-2026-54699
Aliases: GHSA-xmw3-wj6r-48m4
CVSS: 7.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-54699
Type: osv

## Details
Warp is an agentic development environment. From 0.2024.03.12.08.02.stable_01 until 0.2026.05.06.15.42.stable_01, Warp contains an OS command injection vulnerability in the WSL URL-opening fallback. When Warp is running under WSL and cannot open a URL through wslview, it falls back to a Windows command processor path. A URL controlled through terminal output can reach that fallback when the user opens the link. This vulnerability is fixed in 0.2026.05.06.15.42.stable_01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54699.json
- https://github.com/warpdotdev/warp/security/advisories/GHSA-xmw3-wj6r-48m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-54699
- https://github.com/warpdotdev/warp/commit/c66cff48afba73bb1f26f82e5d524018bacb748e
