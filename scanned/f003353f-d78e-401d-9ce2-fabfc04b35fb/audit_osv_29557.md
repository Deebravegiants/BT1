# [H] mlxsw: spectrum_acl_erp: Fix object nesting warning

## Summary
Severity: High
Advisory: CVE-2024-43880
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2024-43880
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mlxsw: spectrum_acl_erp: Fix object nesting warning

ACLs in Spectrum-2 and newer ASICs can reside in the algorithmic TCAM
(A-TCAM) or in the ordinary circuit TCAM (C-TCAM). The former can
contain more ACLs (i.e., tc filters), but the number of masks in each
region (i.e., tc chain) is limited.

In order to mitigate the effects of the above limitation, the device
allows filters to share a single mask if their masks only differ in up
to 8 consecutive bits. For example, dst_ip/25 can be represented using
dst_ip/24 with a delta of 1 bit. The C-TCAM does not have a limit on the
number of masks being used (and therefore does not support mask
aggregation), but can contain a limited number of filters.

The driver uses the "objagg" library to perform the mask aggregation by
passing it objects that consist of the filter's mask and whether the
filter is to be inserted into the A-TCAM or the C-TCAM since filters in
different TCAMs cannot share a mask.

The set of created objects is dependent on the insertion order of the
filters and is not necessarily optimal. Therefore, the driver will
periodically ask the library to compute a more optimal set ("hints") by
looking at all the existing objects.

When the library asks the driver whether two objects can be aggregated
the driver only compares the provided masks and ignores the A-TCAM /
C-TCAM indication. This is the right thing to do since the goal is to
move as many filters as possible to the A-TCAM. The driver also forbids
two identical masks from being aggregated since this can only happen if
one was intentionally put in the C-TCAM to avoid a conflict in the
A-TCAM.

The above can result in the following set of hints:

H1: {mask X, A-TCAM} -> H2: {mask Y, A-TCAM} // X is Y + delta
H3: {mask Y, C-TCAM} -> H4: {mask Z, A-TCAM} // Y is Z + delta

After getting the hints from the library the driver will start migrating
filters from one region to another while consulting the computed hints
and instructing the device to perform a lookup in both regions during
the transition.

Assuming a filter with mask X is being migrated into the A-TCAM in the
new region, the hints lookup will return H1. Since H2 is the parent of
H1, the library will try to find the object associated with it and
create it if necessary in which case another hints lookup (recursive)
will be performed. This hints lookup for {mask Y, A-TCAM} will either
return H2 or H3 since the driver passes the library an object comparison
function that ignores the A-TCAM / C-TCAM indication.

This can eventually lead to nested objects which are not supported by
the library [1].

Fix by removing the object comparison function from both the driver and
the library as the driver was the only user. That way the lookup will
only return exact matches.

I do not have a reliable reproducer that can reproduce the issue in a
timely manner, but before the fix the issue would reproduce in several
minutes and with the fix it does not reproduce in over an hour.

Note that the current usefulness of the hints is limited because they
include the C-TCAM indication and represent aggregation that cannot
actually happen. This will be addressed in net-next.

[1]
WARNING: CPU: 0 PID: 153 at lib/objagg.c:170 objagg_obj_parent_assign+0xb5/0xd0
Modules linked in:
CPU: 0 PID: 153 Comm: kworker/0:18 Not tainted 6.9.0-rc6-custom-g70fbc2c1c38b #42
Hardware name: Mellanox Technologies Ltd. MSN3700C/VMOD0008, BIOS 5.11 10/10/2018
Workqueue: mlxsw_core mlxsw_sp_acl_tcam_vregion_rehash_work
RIP: 0010:objagg_obj_parent_assign+0xb5/0xd0
[...]
Call Trace:
 <TASK>
 __objagg_obj_get+0x2bb/0x580
 objagg_obj_get+0xe/0x80
 mlxsw_sp_acl_erp_mask_get+0xb5/0xf0
 mlxsw_sp_acl_atcam_entry_add+0xe8/0x3c0
 mlxsw_sp_acl_tcam_entry_create+0x5e/0xa0
 mlxsw_sp_acl_tcam_vchunk_migrate_one+0x16b/0x270
 mlxsw_sp_acl_tcam_vregion_rehash_work+0xbe/0x510
 process_one_work+0x151/0x370

## References
- https://git.kernel.org/stable/c/0e59c2d22853266704e127915653598f7f104037
- https://git.kernel.org/stable/c/25c6fd9648ad05da493a5d30881896a78a08b624
- https://git.kernel.org/stable/c/36a9996e020dd5aa325e0ecc55eb2328288ea6bb
- https://git.kernel.org/stable/c/4dc09f6f260db3c4565a4ec52ba369393598f2fb
- https://git.kernel.org/stable/c/97d833ceb27dc19f8777d63f90be4a27b5daeedf
- https://git.kernel.org/stable/c/9a5261a984bba4f583d966c550fa72c33ff3714e
- https://git.kernel.org/stable/c/fb5d4fc578e655d113f09565f6f047e15f7ab578
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43880.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43880
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
