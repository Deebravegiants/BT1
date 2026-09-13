# [M] drm/imagination: Break an object reference loop

## Summary
Severity: Medium
Advisory: CVE-2024-53084
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53084
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/imagination: Break an object reference loop

When remaining resources are being cleaned up on driver close,
outstanding VM mappings may result in resources being leaked, due
to an object reference loop, as shown below, with each object (or
set of objects) referencing the object below it:

    PVR GEM Object
    GPU scheduler "finished" fence
    GPU scheduler “scheduled” fence
    PVR driver “done” fence
    PVR Context
    PVR VM Context
    PVR VM Mappings
    PVR GEM Object

The reference that the PVR VM Context has on the VM mappings is a
soft one, in the sense that the freeing of outstanding VM mappings
is done as part of VM context destruction; no reference counts are
involved, as is the case for all the other references in the loop.

To break the reference loop during cleanup, free the outstanding
VM mappings before destroying the PVR Context associated with the
VM context.

## References
- https://git.kernel.org/stable/c/b04ce1e718bd55302b52d05d6873e233cb3ec7a1
- https://git.kernel.org/stable/c/cb86db12b290ed07d05df00d99fa150bb123e80e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53084.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53084
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
