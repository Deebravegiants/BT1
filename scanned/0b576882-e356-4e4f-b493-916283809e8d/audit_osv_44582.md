# [M] PX4 Autopilot sd_bench Heap Buffer Overflow via Block Size

## Summary
Severity: Medium
Advisory: CVE-2026-84698
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84698
Type: osv

## Details
PX4 Autopilot contains a heap buffer overflow vulnerability in the sd_bench command that writes a four-byte block number into a user-supplied sized allocation. Attackers can invoke sd_bench with a block size below four bytes to overflow the heap buffer and potentially execute code or crash the system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84698.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84698
- https://www.vulncheck.com/advisories/px4-autopilot-sd-bench-heap-buffer-overflow-via-block-size
- https://github.com/PX4/PX4-Autopilot/issues/28373
- https://github.com/PX4/PX4-Autopilot
- https://github.com/PX4/PX4-Autopilot/blob/v1.17.0/src/systemcmds/sd_bench/sd_bench.cpp
