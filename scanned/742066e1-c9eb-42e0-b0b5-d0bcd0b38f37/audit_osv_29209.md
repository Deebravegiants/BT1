# [H] f2fs: remove clear SB_INLINECRYPT flag in default_options

## Summary
Severity: High
Advisory: CVE-2024-40971
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40971
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.96, >=6.2.0 <6.6.36, >=6.7.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: remove clear SB_INLINECRYPT flag in default_options

In f2fs_remount, SB_INLINECRYPT flag will be clear and re-set.
If create new file or open file during this gap, these files
will not use inlinecrypt. Worse case, it may lead to data
corruption if wrappedkey_v0 is enable.

Thread A:                               Thread B:

-f2fs_remount				-f2fs_file_open or f2fs_new_inode
  -default_options
	<- clear SB_INLINECRYPT flag

                                          -fscrypt_select_encryption_impl

  -parse_options
	<- set SB_INLINECRYPT again

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/38a82c8d00638bb642bef787eb1d5e0e4d3b7d71
- https://git.kernel.org/stable/c/724429db09e21ee153fef35e34342279d33df6ae
- https://git.kernel.org/stable/c/a9cea0489c562c97cd56bb345e78939f9909e7f4
- https://git.kernel.org/stable/c/ac5eecf481c29942eb9a862e758c0c8b68090c33
- https://git.kernel.org/stable/c/ae39c8ec4250d2a35ddaab1c40faacfec306ff66
- https://git.kernel.org/stable/c/eddeb8d941d5be11a9da5637dbe81ac37e8449a2
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40971.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40971
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
