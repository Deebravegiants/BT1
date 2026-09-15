# [H] fs: Fix uninitialized 'offp' in statmount_string()

## Summary
Severity: High
Advisory: CVE-2025-68212
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68212
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: Fix uninitialized 'offp' in statmount_string()

In statmount_string(), most flags assign an output offset pointer (offp)
which is later updated with the string offset. However, the
STATMOUNT_MNT_UIDMAP and STATMOUNT_MNT_GIDMAP cases directly set the
struct fields instead of using offp. This leaves offp uninitialized,
leading to a possible uninitialized dereference when *offp is updated.

Fix it by assigning offp for UIDMAP and GIDMAP as well, keeping the code
path consistent.

## References
- https://git.kernel.org/stable/c/0778ac7df5137d5041783fadfc201f8fd55a1d9b
- https://git.kernel.org/stable/c/acfde9400e611c8d2668f1c70053c4a1d6ecfc36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68212.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68212
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
