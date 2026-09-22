# [H] sctp: prevent peer transport count overflow

## Summary
Severity: High
Advisory: CVE-2026-74469
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74469
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: prevent peer transport count overflow

sctp_assoc_add_peer() increments the association's 16-bit transport_count
for every new unique peer. Adding the 65,536th transport wraps the count to
zero.

SCTP sock_diag uses transport_count to reserve the INET_DIAG_PEERS payload,
then copies one sockaddr_storage for every entry in transport_addr_list.
After the wrap, a diagnostic dump reserves an empty payload and writes
8 MiB of peer addresses past the skb tail.

Reject a new unique peer when transport_count has reached U16_MAX. Perform
the check after the existing-peer lookup so a duplicate address continues
to return its existing transport at the limit.

## References
- https://git.kernel.org/stable/c/09e722030e8148ba4ed1e42c6b2ea57bda9f9895
- https://git.kernel.org/stable/c/4ba5bf7ed50f235ea4581de8e7a0002f4ed287b0
- https://git.kernel.org/stable/c/546221b86ceeba0d8fec92d46a0604bb7b62be07
- https://git.kernel.org/stable/c/6201cd1d70f1670c5b31ac506e7ab2fa7b8e7f75
- https://git.kernel.org/stable/c/80f48523a0fe42db2e7375dff4e38a25c117090a
- https://git.kernel.org/stable/c/b453e00da1211e997b82743d28af7714c59c05c8
- https://git.kernel.org/stable/c/bd0e9289e2642f6a5c54faad304ce0f41e926d22
- https://git.kernel.org/stable/c/dfea32dd76f390e3155177b0038cc47b01386198
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74469.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74469
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
