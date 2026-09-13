# [C] tls: fix use-after-free on failed backlog decryption

## Summary
Severity: Critical
Advisory: CVE-2024-26800
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-26800
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.18 <6.6.21, >=6.7.6 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: fix use-after-free on failed backlog decryption

When the decrypt request goes to the backlog and crypto_aead_decrypt
returns -EBUSY, tls_do_decryption will wait until all async
decryptions have completed. If one of them fails, tls_do_decryption
will return -EBADMSG and tls_decrypt_sg jumps to the error path,
releasing all the pages. But the pages have been passed to the async
callback, and have already been released by tls_decrypt_done.

The only true async case is when crypto_aead_decrypt returns
 -EINPROGRESS. With -EBUSY, we already waited so we can tell
tls_sw_recvmsg that the data is available for immediate copy, but we
need to notify tls_decrypt_sg (via the new ->async_done flag) that the
memory has already been released.

## References
- https://git.kernel.org/stable/c/13114dc5543069f7b97991e3b79937b6da05f5b0
- https://git.kernel.org/stable/c/1ac9fb84bc7ecd4bc6428118301d9d864d2a58d1
- https://git.kernel.org/stable/c/81be85353b0f5a7b660635634b655329b429eefe
- https://git.kernel.org/stable/c/f2b85a4cc763841843de693bbd7308fe9a2c4c89
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26800.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26800
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
