# [M] LightFTP 2.3.1 Race Condition DoS via worker_thread_cleanup

## Summary
Severity: Medium
Advisory: CVE-2026-67607
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-67607
Type: osv

## Details
LightFTP 2.3.1 contains a residual race condition vulnerability (an incomplete fix for CVE-2024-11144) in the worker_thread_cleanup() function of ftpserv.c that allows remote unauthenticated attackers to destabilize or crash the daemon by triggering unsynchronized access to shared per-connection state without holding the required mutex lock. Attackers can send a data-transfer command such as LIST followed immediately by ABOR to exploit the missing synchronization on shared context and detached thread id reuse, resulting in daemon destabilization or crash which can lead to a denial of service. The 2.3.1 patch only narrowed the timing window (an extra re-check and reordered cleanup), it never added the missing lock, so the underlying race remains.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67607.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67607
- https://www.vulncheck.com/advisories/lightftp-race-condition-dos-via-worker-thread-cleanup
- https://github.com/hfiref0x/LightFTP
- https://github.com/zeroscience/tuktam#real-world-case-study-lightftp-cve-2024-11144
