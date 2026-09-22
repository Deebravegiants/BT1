# [M] wb2osz/direwolf <= 1.8.1 Reachable Assertion DoS

## Summary
Severity: Medium
Advisory: CVE-2025-34458
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-22
Source: https://osv.dev/vulnerability/CVE-2025-34458
Type: osv

## Details
wb2osz/direwolf (Dire Wolf) versions up to and including 1.8, prior to commit 3658a87, contain a reachable assertion vulnerability in the APRS MIC-E decoder function aprs_mic_e() located in src/decode_aprs.c. When processing a specially crafted AX.25 frame containing a MIC-E message with an empty or truncated comment field, the application triggers an unhandled assertion checking for a non-empty comment. This assertion failure causes immediate process termination, allowing a remote, unauthenticated attacker to cause a denial of service by sending malformed APRS traffic.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34458.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34458
- https://www.vulncheck.com/advisories/wb2osz-direwolf-reachable-assertion-dos
- https://github.com/wb2osz/direwolf/issues/618
- https://github.com/wb2osz/direwolf/commit/3658a87
- https://github.com/wb2osz/direwolf
- https://github.com/marlinkcyber/advisories/blob/main/advisories/MCSAID-2025-010-direwolf-stack-buffer-overflow-kiss-frame.md
