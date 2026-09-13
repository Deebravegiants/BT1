# [H] nvmet-tcp: check return value of nvmet_tcp_set_queue_sock

## Summary
Severity: High
Advisory: CVE-2026-74385
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74385
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-tcp: check return value of nvmet_tcp_set_queue_sock

The return value of nvmet_tcp_set_queue_sock() is currently ignored in
nvmet_tcp_tls_handshake_done(). If it fails (e.g., due to the socket
not being in TCP_ESTABLISHED state), the socket callbacks will not be
properly set, leading to queue and socket leakage.

Fix this by capturing the return value and calling
nvmet_tcp_schedule_release_queue() on failure to ensure proper cleanup.

## References
- https://git.kernel.org/stable/c/22aa70f9a0544643ec37d442b6fcb1833d804462
- https://git.kernel.org/stable/c/7ef789703e2b91775dcb36b2efa46325be31a2a0
- https://git.kernel.org/stable/c/cba2ee57fd302727aea7d41e9d9cd0969f5df0fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74385.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74385
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
