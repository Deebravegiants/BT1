# [H] smb/client: fix possible infinite loop and oob read in symlink_data()

## Summary
Severity: High
Advisory: CVE-2026-52967
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52967
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb/client: fix possible infinite loop and oob read in symlink_data()

On 32-bit architectures, the infinite loop is as follows:

  len = p->ErrorDataLength == 0xfffffff8
  u8 *next = p->ErrorContextData + len
  next == p

On 32-bit architectures, the out-of-bounds read is as follows:

  len = p->ErrorDataLength == 0xfffffff0
  u8 *next = p->ErrorContextData + len
  next == (u8 *)p - 8

## References
- https://git.kernel.org/stable/c/1b9331b16b0ed9414dcf7583d8134bdfeb117aae
- https://git.kernel.org/stable/c/1cfa2d59f669db28d6292d10ff87ca6837c781b0
- https://git.kernel.org/stable/c/7d9a7f1f96cd617ee9e75bb22217c709038e26b8
- https://git.kernel.org/stable/c/97a05b0ae9ea5ec052be2eef0f9cc7ce03501bbb
- https://git.kernel.org/stable/c/b41598bf54b3fe528994e573df6008f8f4d0a4f4
- https://git.kernel.org/stable/c/cd4b9b662f0fb9aa97ee6bf9034eca76fc6cab23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52967.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52967
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
