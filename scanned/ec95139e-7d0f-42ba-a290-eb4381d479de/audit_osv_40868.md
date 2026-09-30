# [M] net: ip/tcp: Null pointer dereference can be triggered by a race condition

## Summary
Severity: Medium
Advisory: CVE-2026-5590
Aliases: GHSA-4vqm-pw24-g9jp
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-04-05
Source: https://osv.dev/vulnerability/CVE-2026-5590
Type: osv

## Details
A race condition during TCP connection teardown can cause tcp_recv() to operate on a connection that has already been released. If tcp_conn_search() returns NULL while processing a SYN packet, a NULL pointer derived from stale context data is passed to tcp_backlog_is_full() and dereferenced without validation, leading to a crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5590.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-4vqm-pw24-g9jp
- https://nvd.nist.gov/vuln/detail/CVE-2026-5590
- https://github.com/zephyrproject-rtos/zephyr
