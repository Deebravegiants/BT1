# [H] smb: client: fix in-place encryption corruption in SMB2_write()

## Summary
Severity: High
Advisory: CVE-2026-43362
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43362
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix in-place encryption corruption in SMB2_write()

SMB2_write() places write payload in iov[1..n] as part of rq_iov.
smb3_init_transform_rq() pointer-shares rq_iov, so crypt_message()
encrypts iov[1] in-place, replacing the original plaintext with
ciphertext. On a replayable error, the retry sends the same iov[1]
which now contains ciphertext instead of the original data,
resulting in corruption.

The corruption is most likely to be observed when connections are
unstable, as reconnects trigger write retries that re-send the
already-encrypted data.

This affects SFU mknod, MF symlinks, etc. On kernels before
6.10 (prior to the netfs conversion), sync writes also used
this path and were similarly affected. The async write path
wasn't unaffected as it uses rq_iter which gets deep-copied.

Fix by moving the write payload into rq_iter via iov_iter_kvec(),
so smb3_init_transform_rq() deep-copies it before encryption.

## References
- https://git.kernel.org/stable/c/438e77435aee2894d5edf90be5c87004a57f6258
- https://git.kernel.org/stable/c/52327268224fb9ccc7ecfbbdfdfff54b6e93c518
- https://git.kernel.org/stable/c/92e64f1852f455f57d0850989e57c30d7fac7d95
- https://git.kernel.org/stable/c/aea5e37388a080361110ab5790f57ae0af383650
- https://git.kernel.org/stable/c/d78840a6a38d312dc1a51a65317bb67e46f0b929
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43362.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43362
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
