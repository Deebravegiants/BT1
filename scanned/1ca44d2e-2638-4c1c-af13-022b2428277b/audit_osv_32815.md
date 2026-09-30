# [H] __legitimize_mnt(): check for MNT_SYNC_UMOUNT should be under mount_lock

## Summary
Severity: High
Advisory: CVE-2025-38058
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38058
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.185, >=5.16.0 <6.1.141, >=6.2.0 <6.6.93, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

__legitimize_mnt(): check for MNT_SYNC_UMOUNT should be under mount_lock

... or we risk stealing final mntput from sync umount - raising mnt_count
after umount(2) has verified that victim is not busy, but before it
has set MNT_SYNC_UMOUNT; in that case __legitimize_mnt() doesn't see
that it's safe to quietly undo mnt_count increment and leaves dropping
the reference to caller, where it'll be a full-blown mntput().

Check under mount_lock is needed; leaving the current one done before
taking that makes no sense - it's nowhere near common enough to bother
with.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/250cf3693060a5f803c5f1ddc082bb06b16112a9
- https://git.kernel.org/stable/c/628fb00195ce21a90cf9e4e3d105cd9e58f77b40
- https://git.kernel.org/stable/c/8cafd7266fa02e0863bacbf872fe635c0b9725eb
- https://git.kernel.org/stable/c/9b0915e72b3cf52474dcee0b24a2f99d93e604a3
- https://git.kernel.org/stable/c/b55996939c71a3e1a38f3cdc6a8859797efc9083
- https://git.kernel.org/stable/c/b89eb56a378b7b2c1176787fc228d0a57172bdd5
- https://git.kernel.org/stable/c/d8ece4ced3b051e656c77180df2e69e19e24edc1
- https://git.kernel.org/stable/c/f6d45fd92f62845cbd1eb5128fd8f0ed7d0c5a42
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38058.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38058
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
