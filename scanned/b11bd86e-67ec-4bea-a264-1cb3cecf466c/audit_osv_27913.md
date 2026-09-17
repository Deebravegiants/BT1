# [H] ext4: avoid allocating blocks from corrupted group in ext4_mb_find_by_goal()

## Summary
Severity: High
Advisory: CVE-2024-26772
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26772
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <4.19.308, >=4.20.0 <5.4.270, >=5.5.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: avoid allocating blocks from corrupted group in ext4_mb_find_by_goal()

Places the logic for checking if the group's block bitmap is corrupt under
the protection of the group lock to avoid allocating blocks from the group
with a corrupted block bitmap.

## References
- https://git.kernel.org/stable/c/21dbe20589c7f48e9c5d336ce6402bcebfa6d76a
- https://git.kernel.org/stable/c/5a6dcc4ad0f7f7fa8e8d127b5526e7c5f2d38a43
- https://git.kernel.org/stable/c/6b92b1bc16d691c95b152c6dbf027ad64315668d
- https://git.kernel.org/stable/c/832698373a25950942c04a512daa652c18a9b513
- https://git.kernel.org/stable/c/8de8305a25bfda607fc13475ebe84b978c96d7ff
- https://git.kernel.org/stable/c/d3bbe77a76bc52e9d4d0a120f1509be36e25c916
- https://git.kernel.org/stable/c/d639102f4cbd4cb65d1225dba3b9265596aab586
- https://git.kernel.org/stable/c/ffeb72a80a82aba59a6774b0611f792e0ed3b0b7
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26772.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26772
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
