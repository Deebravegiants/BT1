# [C] libceph: Avoid using invalid osd indices from primary_temp

## Summary
Severity: Critical
Advisory: CVE-2026-80558
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80558
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: Avoid using invalid osd indices from primary_temp

A corrupted osdmap received from a Ceph monitor or OSD may contain osd
indices in its pg_temp, primary_temp, pg_upmap, and pg_upmap_items parts
that don't exist, i.e., that are greater than max_osd or smaller than
CEPH_HOMELESS_OSD (-1). These indices are used to create the up and
acting set in ceph_pg_to_up_acting_osds(), called from calc_target().
While most of these osd indices are checked, the one from primary_temp
is not. Subsequently, this may lead to calc_target() returning this
(potentially invalid) index as target osd for a (linger) request.
Because the osd_state, osd_weight, and osd_addr arrays only contain
max_osd entries (with indices 0 to max_osd -1), this leads to
out-of-bounds accesses when trying to read values from these arrays.

This patch fixes the issue by adding a check to get_temp_osds(), so that
only valid osd indices from primary_temp are used, and it falls back to
using the primary from pg_temp or the up set if it is invalid.

[ idryomov: changelog ]

## References
- https://git.kernel.org/stable/c/1c705fe8e59c6b16f48964973fb23c8ec4735b73
- https://git.kernel.org/stable/c/3660b98d1204b419f6a77e9a295f148dcf38d042
- https://git.kernel.org/stable/c/4f392fec075562dc93bb0c69f37423ca2af9b48f
- https://git.kernel.org/stable/c/505fc50b8ff8e687b7e3ef6866269dea27366224
- https://git.kernel.org/stable/c/6799d4a916ffcb3d450d8440f9fe0f0862f768d6
- https://git.kernel.org/stable/c/dfe1877d351b99eb1b1a62a3fc2d174220e88e20
- https://git.kernel.org/stable/c/e009c5f0ad634c62f5c48a41f1f3c019ecf52555
- https://git.kernel.org/stable/c/e2ffeec85201b2bb748e99e12539ee1b92f62796
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80558.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80558
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
