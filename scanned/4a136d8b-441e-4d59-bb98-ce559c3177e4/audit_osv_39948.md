# [M] CVE-2026-48693

## Summary
Severity: Medium
Advisory: CVE-2026-48693
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-48693
Type: osv

## Details
FastNetMon Community Edition through 1.2.9 is vulnerable to a local symlink attack via predictable file paths in /tmp. The statistics file path defaults to '/tmp/fastnetmon.dat' (src/fastnetmon.cpp line 159). The print_screen_contents_into_file() function (src/fastnetmon_logic.cpp line 2186) opens this path with std::ios::trunc without checking for symlinks or using O_NOFOLLOW. Additionally, the chmod() call on line 2190 always operates on cli_stats_file_path regardless of which file_path parameter was passed (a bug that applies wrong permissions), and the umask is set to 0 during daemonization (src/fastnetmon.cpp line 1821), making all created files world-writable. A local attacker can exploit this to overwrite arbitrary files as the FastNetMon process user (typically root).

## References
- https://github.com/pavel-odintsov/fastnetmon/blob/master/src/fastnetmon.cpp
- https://github.com/pavel-odintsov/fastnetmon/blob/master/src/fastnetmon_logic.cpp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48693.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48693
- https://github.com/pavel-odintsov/fastnetmon
- https://lorikeetsecurity.com/blog/fastnetmon-cve-2026-48693-symlink-tmp
