# [C] ksmbd: fix use-after-free from async crypto on Qualcomm crypto engine

## Summary
Severity: Critical
Advisory: CVE-2026-53046
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53046
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free from async crypto on Qualcomm crypto engine

ksmbd_crypt_message() sets a NULL completion callback on AEAD requests
and does not handle the -EINPROGRESS return code from async hardware
crypto engines like the Qualcomm Crypto Engine (QCE). When QCE returns
-EINPROGRESS, ksmbd treats it as an error and immediately frees the
request while the hardware DMA operation is still in flight. The DMA
completion callback then dereferences freed memory, causing a NULL
pointer crash:

  pc : qce_skcipher_done+0x24/0x174
  lr : vchan_complete+0x230/0x27c
  ...
  el1h_64_irq+0x68/0x6c
  ksmbd_free_work_struct+0x20/0x118 [ksmbd]
  ksmbd_exit_file_cache+0x694/0xa4c [ksmbd]

Use the standard crypto_wait_req() pattern with crypto_req_done() as
the completion callback, matching the approach used by the SMB client
in fs/smb/client/smb2ops.c. This properly handles both synchronous
engines (immediate return) and async engines (-EINPROGRESS followed
by callback notification).

## References
- https://git.kernel.org/stable/c/3e298897f41c61450c2e7a4f457e8b2485eb35b3
- https://git.kernel.org/stable/c/57b47231055b431ed0a1a55f33cac32981564405
- https://git.kernel.org/stable/c/7164b3953cefd540e7ebca828c793bc6869cfbc4
- https://git.kernel.org/stable/c/8ef183216feaa24b66b940510d8b68f680eb56e9
- https://git.kernel.org/stable/c/8fcefe840fa8c14ce667768e5b043286ac3bbcbe
- https://git.kernel.org/stable/c/b46aa129fa2807bfe1545fe74d9295d53c51520b
- https://git.kernel.org/stable/c/cc2da381875d4a67026e4c8feb3dba51a2a2d1bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53046.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53046
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
