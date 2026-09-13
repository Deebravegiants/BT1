# [M] radare2 6.1.5 Use-After-Free via gdbr_threads_list()

## Summary
Severity: Medium
Advisory: CVE-2026-8695
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-8695
Type: osv

## Details
radare2 6.1.5 contains a use-after-free vulnerability in the gdbr_threads_list() function that allows remote attackers to trigger memory corruption by sending a valid qfThreadInfo response followed by a malformed qsThreadInfo response. Attackers can exploit this vulnerability through GDB remote debugging to cause a denial of service or potentially achieve code execution by manipulating thread list processing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8695.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8695
- https://www.vulncheck.com/advisories/radare2-use-after-free-via-gdbr-threads-list
- https://github.com/radareorg/radare2/issues/25835
- https://github.com/radareorg/radare2/issues/25836
- https://github.com/radareorg/radare2/commit/c213ad6894a1eb9086ac8bf5fae35757e9e1683c
