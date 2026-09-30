# [M] nilfs2: fix kernel bug due to missing clearing of buffer delay flag

## Summary
Severity: Medium
Advisory: CVE-2024-50116
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50116
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix kernel bug due to missing clearing of buffer delay flag

Syzbot reported that after nilfs2 reads a corrupted file system image
and degrades to read-only, the BUG_ON check for the buffer delay flag
in submit_bh_wbc() may fail, causing a kernel bug.

This is because the buffer delay flag is not cleared when clearing the
buffer state flags to discard a page/folio or a buffer head. So, fix
this.

This became necessary when the use of nilfs2's own page clear routine
was expanded.  This state inconsistency does not occur if the buffer
is written normally by log writing.

## References
- https://git.kernel.org/stable/c/033bc52f35868c2493a2d95c56ece7fc155d7cb3
- https://git.kernel.org/stable/c/27524f65621f490184f2ace44cd8e5f3685af4a3
- https://git.kernel.org/stable/c/412a30b1b28d6073ba29c46a2b0f324c5936293f
- https://git.kernel.org/stable/c/6ed469df0bfbef3e4b44fca954a781919db9f7ab
- https://git.kernel.org/stable/c/743c78d455e784097011ea958b27396001181567
- https://git.kernel.org/stable/c/822203f6355f4b322d21e7115419f6b98284be25
- https://git.kernel.org/stable/c/9f2ab98371c2f2488bf3bf3f9b2a73510545e9c1
- https://git.kernel.org/stable/c/c6f58ff2d4c552927fe9a187774e668ebba6c7aa
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50116.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50116
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
