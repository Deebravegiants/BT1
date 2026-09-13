# [C] net/tls: fix use-after-free in -EBUSY error path of tls_do_encryption

## Summary
Severity: Critical
Advisory: CVE-2026-31533
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-31533
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.8.0 <6.18.23, >=6.13.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/tls: fix use-after-free in -EBUSY error path of tls_do_encryption

The -EBUSY handling in tls_do_encryption(), introduced by commit
859054147318 ("net: tls: handle backlogging of crypto requests"), has
a use-after-free due to double cleanup of encrypt_pending and the
scatterlist entry.

When crypto_aead_encrypt() returns -EBUSY, the request is enqueued to
the cryptd backlog and the async callback tls_encrypt_done() will be
invoked upon completion. That callback unconditionally restores the
scatterlist entry (sge->offset, sge->length) and decrements
ctx->encrypt_pending. However, if tls_encrypt_async_wait() returns an
error, the synchronous error path in tls_do_encryption() performs the
same cleanup again, double-decrementing encrypt_pending and
double-restoring the scatterlist.

The double-decrement corrupts the encrypt_pending sentinel (initialized
to 1), making tls_encrypt_async_wait() permanently skip the wait for
pending async callbacks. A subsequent sendmsg can then free the
tls_rec via bpf_exec_tx_verdict() while a cryptd callback is still
pending, resulting in a use-after-free when the callback fires on the
freed record.

Fix this by skipping the synchronous cleanup when the -EBUSY async
wait returns an error, since the callback has already handled
encrypt_pending and sge restoration.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/02f3ecadb23558bbe068e6504118f1b712d4ece0
- https://git.kernel.org/stable/c/0e43e0a3c94044acc74b8e0927c27972eb5a59e8
- https://git.kernel.org/stable/c/2694d408b0e595024e0fc1d64ff9db0358580f74
- https://git.kernel.org/stable/c/414fc5e5a5aff776c150f1b86770e0a25a35df3a
- https://git.kernel.org/stable/c/5d70eb25b41e9b010828cd12818b06a0c3b04412
- https://git.kernel.org/stable/c/a9b8b18364fffce4c451e6f6fd218fa4ab646705
- https://git.kernel.org/stable/c/aa9facde6c5005205874c37db3fd25799d741baf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31533.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31533
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
