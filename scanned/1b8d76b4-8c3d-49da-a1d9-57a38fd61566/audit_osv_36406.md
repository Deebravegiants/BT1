# [H] tls: Purge async_hold in tls_decrypt_async_wait()

## Summary
Severity: High
Advisory: CVE-2026-23414
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-23414
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.18.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: Purge async_hold in tls_decrypt_async_wait()

The async_hold queue pins encrypted input skbs while
the AEAD engine references their scatterlist data. Once
tls_decrypt_async_wait() returns, every AEAD operation
has completed and the engine no longer references those
skbs, so they can be freed unconditionally.

A subsequent patch adds batch async decryption to
tls_sw_read_sock(), introducing a new call site that
must drain pending AEAD operations and release held
skbs. Move __skb_queue_purge(&ctx->async_hold) into
tls_decrypt_async_wait() so the purge is centralized
and every caller -- recvmsg's drain path, the -EBUSY
fallback in tls_do_decryption(), and the new read_sock
batch path -- releases held skbs on synchronization
without each site managing the purge independently.

This fixes a leak when tls_strp_msg_hold() fails part-way through,
after having added some cloned skbs to the async_hold
queue. tls_decrypt_sg() will then call tls_decrypt_async_wait() to
process all pending decrypts, and drop back to synchronous mode, but
tls_sw_recvmsg() only flushes the async_hold queue when one record has
been processed in "fully-async" mode, which may not be the case here.

[pabeni@redhat.com: added leak comment]

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/2dcf324855c34e7f934ce978aa19b645a8f3ee71
- https://git.kernel.org/stable/c/6dc11e0bd0a5466bcc76d275c09e5537bd0597dd
- https://git.kernel.org/stable/c/84a8335d8300576f1b377ae24abca1d9f197807f
- https://git.kernel.org/stable/c/9f557c7eae127b44d2e863917dc986a4b6cb1269
- https://git.kernel.org/stable/c/ac435be7c7613eb13a5a8ceb5182e10b50c9ce87
- https://git.kernel.org/stable/c/fd8037e1f18ca5336934d0e0e7e1a4fe097e749d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23414.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23414
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
