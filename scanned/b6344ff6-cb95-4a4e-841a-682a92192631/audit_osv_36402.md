# [H] apparmor: fix race on rawdata dereference

## Summary
Severity: High
Advisory: CVE-2026-23410
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-23410
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.18, >=6.19.0 <6.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: fix race on rawdata dereference

There is a race condition that leads to a use-after-free situation:
because the rawdata inodes are not refcounted, an attacker can start
open()ing one of the rawdata files, and at the same time remove the
last reference to this rawdata (by removing the corresponding profile,
for example), which frees its struct aa_loaddata; as a result, when
seq_rawdata_open() is reached, i_private is a dangling pointer and
freed memory is accessed.

The rawdata inodes weren't refcounted to avoid a circular refcount and
were supposed to be held by the profile rawdata reference.  However
during profile removal there is a window where the vfs and profile
destruction race, resulting in the use after free.

Fix this by moving to a double refcount scheme. Where the profile
refcount on rawdata is used to break the circular dependency. Allowing
for freeing of the rawdata once all inode references to the rawdata
are put.

## References
- https://git.kernel.org/stable/c/3b8e77c7abab40e6de9ad9de730d77984a498840
- https://git.kernel.org/stable/c/6b6ba87579c7e7c669e0bec91823e7fb693bc5df
- https://git.kernel.org/stable/c/6ef1f2926c41ab96952d9696d55a052f1b3a9418
- https://git.kernel.org/stable/c/763e838adc3c7ec5a7df2990ce84cad951e42721
- https://git.kernel.org/stable/c/a0b7091c4de45a7325c8780e6934a894f92ac86b
- https://git.kernel.org/stable/c/af782cc8871e3683ddd5a3cd2f7df526599863a9
- https://git.kernel.org/stable/c/d9d8560b9b7932f8cffc4c068c14289220900f79
- https://git.kernel.org/stable/c/f9761add6d100962a23996cb68f3d6abdd4d1815
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23410.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23410
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
