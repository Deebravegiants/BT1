# [C] tls: rx: restore msg_iter before TLS 1.3 optimistic retry

## Summary
Severity: Critical
Advisory: CVE-2026-74611
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74611
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: rx: restore msg_iter before TLS 1.3 optimistic retry

tls_decrypt_sg() advances msg->msg_iter when it maps user pages for
the optimistic TLS 1.3 zero-copy path. If the decrypted record turns
out not to be unpadded application data, tls_decrypt_sw() retries into
a kernel skb, but leaves the iterator advanced.

The subsequent copy from the skb then writes decrypted bytes again at
a later point in the caller iovecs while recvmsg() reports only the
post-retry length. A TLS peer can trigger this after the receiver
enables TLS_RX_EXPECT_NO_PAD.

Revert the iterator by the number of bytes consumed by the optimistic
mapping before retrying without zero-copy.

Add a selftest which sends a TLS 1.3 control record with
TLS_RX_EXPECT_NO_PAD enabled and verifies that recvmsg() does not
overwrite later iovecs beyond the returned length.

## References
- https://git.kernel.org/stable/c/1c8629651cb54f7b51db8fc0b1a9944e4a4b0f5e
- https://git.kernel.org/stable/c/3c837266a734e2a22b24d2d567404a501d405835
- https://git.kernel.org/stable/c/68787940274ec89f41dc91b1a68ee1a16a90735f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74611.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74611
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
