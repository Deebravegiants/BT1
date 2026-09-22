# [M] CVE-2019-18885

## Summary
Severity: Medium
Advisory: CVE-2019-18885
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-14
Source: https://osv.dev/vulnerability/CVE-2019-18885
Type: osv

## Details
fs/btrfs/volumes.c in the Linux kernel before 5.1 allows a btrfs_verify_dev_extents NULL pointer dereference via a crafted btrfs image because fs_devices->devices is mishandled within find_device, aka CID-09ba3bc9dd15.

## References
- https://usn.ubuntu.com/4254-1/
- https://usn.ubuntu.com/4254-2/
- https://usn.ubuntu.com/4287-1/
- https://usn.ubuntu.com/4287-2/
- http://packetstormsecurity.com/files/156185/Kernel-Live-Patch-Security-Notice-LSN-0062-1.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00019.html
- https://usn.ubuntu.com/4258-1/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=09ba3bc9dd150457c506e4661380a6183af651c1
- https://github.com/torvalds/linux/commit/09ba3bc9dd150457c506e4661380a6183af651c1
- https://github.com/bobfuzzer/CVE-2019-18885
