# [H] libceph: replace BUG_ON with bounds check for map->max_osd

## Summary
Severity: High
Advisory: CVE-2025-68283
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68283
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <6.1.159, >=6.2.0 <6.6.119, >=6.7.0 <6.12.61, >=6.13.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: replace BUG_ON with bounds check for map->max_osd

OSD indexes come from untrusted network packets. Boundary checks are
added to validate these against map->max_osd.

[ idryomov: drop BUG_ON in ceph_get_primary_affinity(), minor cosmetic
  edits ]

## References
- https://git.kernel.org/stable/c/57f5fbae9f1024aba17ff75e00433324115c548a
- https://git.kernel.org/stable/c/b4368b7f97014e1015445d61abd0b27c4c6e8424
- https://git.kernel.org/stable/c/becc488a4d864db338ebd4e313aa3c77da24b604
- https://git.kernel.org/stable/c/e67e3be690f5f7e3b031cf29e8d91e6d02a8e30d
- https://git.kernel.org/stable/c/ec3797f043756a94ea2d0f106022e14ac4946c02
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68283.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68283
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
