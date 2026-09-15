# [M] CVE-2023-4385

## Summary
Severity: Medium
Advisory: CVE-2023-4385
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-16
Source: https://osv.dev/vulnerability/CVE-2023-4385
Type: osv

## Details
A NULL pointer dereference flaw was found in dbFree in fs/jfs/jfs_dmap.c in the journaling file system (JFS) in the Linux Kernel. This issue may allow a local attacker to crash the system due to a missing sanity check.

## References
- https://access.redhat.com/security/cve/CVE-2023-4385
- https://bugzilla.redhat.com/show_bug.cgi?id=2219272
- https://github.com/torvalds/linux/commit/0d4837fdb796f99369cf7691d33de1b856bcaf1f
