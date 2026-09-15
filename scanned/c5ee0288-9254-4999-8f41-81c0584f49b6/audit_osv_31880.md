# [C] nvme-tcp: fix potential memory corruption in nvme_tcp_recv_pdu()

## Summary
Severity: Critical
Advisory: CVE-2025-21927
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21927
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-tcp: fix potential memory corruption in nvme_tcp_recv_pdu()

nvme_tcp_recv_pdu() doesn't check the validity of the header length.
When header digests are enabled, a target might send a packet with an
invalid header length (e.g. 255), causing nvme_tcp_verify_hdgst()
to access memory outside the allocated area and cause memory corruptions
by overwriting it with the calculated digest.

Fix this by rejecting packets with an unexpected header length.

## References
- https://git.kernel.org/stable/c/22b06c89aa6b2d1ecb8aea72edfb9d53af8d5126
- https://git.kernel.org/stable/c/9fbc953d6b38bc824392e01850f0aeee3b348722
- https://git.kernel.org/stable/c/ad95bab0cd28ed77c2c0d0b6e76e03e031391064
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21927.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21927
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
