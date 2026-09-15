# [M] CVE-2023-4394

## Summary
Severity: Medium
Advisory: CVE-2023-4394
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-08-17
Source: https://osv.dev/vulnerability/CVE-2023-4394
Type: osv

## Details
A use-after-free flaw was found in btrfs_get_dev_args_from_path in fs/btrfs/volumes.c in btrfs file-system in the Linux Kernel. This flaw allows a local attacker with special privileges to cause a system crash or leak internal kernel information

## References
- https://access.redhat.com/security/cve/CVE-2023-4394
- https://bugzilla.redhat.com/show_bug.cgi?id=2219263
- https://patchwork.kernel.org/project/linux-btrfs/patch/20220815151606.3479183-1-r33s3n6@gmail.com/
