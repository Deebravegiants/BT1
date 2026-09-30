# [H] fs: jfs: fix shift-out-of-bounds in dbAllocAG

## Summary
Severity: High
Advisory: CVE-2022-50567
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2022-50567
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: jfs: fix shift-out-of-bounds in dbAllocAG

Syzbot found a crash : UBSAN: shift-out-of-bounds in dbAllocAG. The
underlying bug is the missing check of bmp->db_agl2size. The field can
be greater than 64 and trigger the shift-out-of-bounds.

Fix this bug by adding a check of bmp->db_agl2size in dbMount since this
field is used in many following functions. The upper bound for this
field is L2MAXL2SIZE - L2MAXAG, thanks for the help of Dave Kleikamp.
Note that, for maintenance, I reorganized error handling code of dbMount.

## References
- https://git.kernel.org/stable/c/0536f76a2bca83d1a3740517ba22cc93a44b3099
- https://git.kernel.org/stable/c/2c575c8905f7a8b32d5611b91856b69bac2a5bf1
- https://git.kernel.org/stable/c/3115313cf03113e87c87adee18ee49a20bbdb9ba
- https://git.kernel.org/stable/c/359616ce587e524107730504891afa4b1a8be58c
- https://git.kernel.org/stable/c/3e997e4ce8ae7ab89d72334120f6aee49c5bbdbd
- https://git.kernel.org/stable/c/67973caae78e21ee46a7281aaa8ca364eb9c444f
- https://git.kernel.org/stable/c/898f706695682b9954f280d95e49fa86ffa55d08
- https://git.kernel.org/stable/c/d3b486946a4e62c7ef6023f7d9c1d049051384ba
- https://git.kernel.org/stable/c/eea87acb6027be3dd4d3c57186bb22800d57fdda
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50567.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50567
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
