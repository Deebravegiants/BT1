# [H] net/tls: fix kernel panic when alloc_page failed

## Summary
Severity: High
Advisory: CVE-2025-38018
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38018
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.140, >=6.2.0 <6.6.92, >=6.7.0 <6.12.30, >=6.13.0 <6.14.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/tls: fix kernel panic when alloc_page failed

We cannot set frag_list to NULL pointer when alloc_page failed.
It will be used in tls_strp_check_queue_ok when the next time
tls_strp_read_sock is called.

This is because we don't reset full_len in tls_strp_flush_anchor_copy()
so the recv path will try to continue handling the partial record
on the next call but we dettached the rcvq from the frag list.
Alternative fix would be to reset full_len.

Unable to handle kernel NULL pointer dereference
at virtual address 0000000000000028
 Call trace:
 tls_strp_check_rcv+0x128/0x27c
 tls_strp_data_ready+0x34/0x44
 tls_data_ready+0x3c/0x1f0
 tcp_data_ready+0x9c/0xe4
 tcp_data_queue+0xf6c/0x12d0
 tcp_rcv_established+0x52c/0x798

## References
- https://git.kernel.org/stable/c/406d05da26835943568e61bb751c569efae071d4
- https://git.kernel.org/stable/c/491deb9b8c4ad12fe51d554a69b8165b9ef9429f
- https://git.kernel.org/stable/c/5f1f833cb388592bb46104463a1ec1b7c41975b6
- https://git.kernel.org/stable/c/8f7f96549bc55e4ef3a6b499bc5011e5de2f46c4
- https://git.kernel.org/stable/c/a11b8c0be6acd0505a58ff40d474bd778b25b93a
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38018.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38018
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
