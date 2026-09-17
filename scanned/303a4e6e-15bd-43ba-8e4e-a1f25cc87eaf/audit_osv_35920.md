# [H] net: eswifi socket send payload length not bounded

## Summary
Severity: High
Advisory: CVE-2026-1679
Aliases: GHSA-qx3g-5g22-fq5w
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-1679
Type: osv

## Details
The eswifi socket offload driver copies user-provided payloads into a fixed buffer without checking available space; oversized sends overflow `eswifi->buf`, corrupting kernel memory (CWE-120). Exploit requires local code that can call the socket send API; no remote attacker can reach it directly.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1679.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-qx3g-5g22-fq5w
- https://nvd.nist.gov/vuln/detail/CVE-2026-1679
- https://github.com/zephyrproject-rtos/zephyr
