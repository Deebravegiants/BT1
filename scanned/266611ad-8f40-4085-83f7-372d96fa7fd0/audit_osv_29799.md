# [H] udf: Avoid excessive partition lengths

## Summary
Severity: High
Advisory: CVE-2024-46777
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46777
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.322, >=4.20.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: Avoid excessive partition lengths

Avoid mounting filesystems where the partition would overflow the
32-bits used for block number. Also refuse to mount filesystems where
the partition length is so large we cannot safely index bits in a
block bitmap.

## References
- https://git.kernel.org/stable/c/0173999123082280cf904bd640015951f194a294
- https://git.kernel.org/stable/c/1497a4484cdb2cf6c37960d788fb6ba67567bdb7
- https://git.kernel.org/stable/c/2ddf831451357c6da4b64645eb797c93c1c054d1
- https://git.kernel.org/stable/c/551966371e17912564bc387fbeb2ac13077c3db1
- https://git.kernel.org/stable/c/925fd8ee80d5348a5e965548e5484d164d19221d
- https://git.kernel.org/stable/c/a56330761950cb83de1dfb348479f20c56c95f90
- https://git.kernel.org/stable/c/c0c23130d38e8bc28e9ef581443de9b1fc749966
- https://git.kernel.org/stable/c/ebbe26fd54a9621994bc16b14f2ba8f84c089693
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46777.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46777
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
