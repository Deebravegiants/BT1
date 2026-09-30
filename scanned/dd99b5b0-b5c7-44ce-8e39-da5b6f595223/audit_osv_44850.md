# [M] radare2 6.1.5 Use-After-Free via gdbr_pids_list()

## Summary
Severity: Medium
Advisory: CVE-2026-8696
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-8696
Type: osv

## Details
radare2 6.1.5 contains a use-after-free vulnerability in the gdbr_pids_list() function within the GDB client core that allows remote attackers to cause a denial of service or potentially execute arbitrary code by sending malformed thread information responses. Attackers can trigger the vulnerability by causing qsThreadInfo to fail after qfThreadInfo successfully allocates RDebugPid structures, resulting in double-free memory corruption when the error path attempts to clean up the list.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8696.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8696
- https://www.vulncheck.com/advisories/radare2-use-after-free-via-gdbr-pids-list
- https://github.com/radareorg/radare2/issues/25836
- https://github.com/radareorg/radare2/commit/c213ad6894a1eb9086ac8bf5fae35757e9e1683c
