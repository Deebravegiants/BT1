# [M] Division by zero in Zephyr ext2 superblock parsing allows DoS via crafted filesystem image

## Summary
Severity: Medium
Advisory: CVE-2026-7007
Aliases: GHSA-wrf2-79mm-cvw5
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-7007
Type: osv

## Details
The Zephyr ext2 file system validates the on-disk superblock in ext2_verify_disk_superblock() (subsys/fs/ext2/ext2_impl.c) before completing a mount. The validator checked the magic number, block size, revision and feature flags, but did not verify that the on-disk fields s_blocks_per_group and s_inodes_per_group are non-zero. Both fields are read directly from the image and are later used as divisors during mount-time initialization.

During mount, get_ngroups() divides and modulos s_blocks_count by s_blocks_per_group (reached via ext2_fetch_block_group() from ext2_init_fs()), and get_itable_entry() divides (ino - 1) by s_inodes_per_group when fetching the root inode (both in subsys/fs/ext2/ext2_diskops.c). A superblock with either field set to zero therefore causes an integer division by zero during the mount sequence.

An attacker who can present a crafted ext2 image to a device that mounts ext2 — removable media such as an SD card or a USB mass-storage device — can trigger this. On ARMv7-M / ARMv8-M-mainline Cortex-M targets, divide-by-zero trapping is enabled (SCB_CCR_DIV_0_TRP), so the division raises a UsageFault that Zephyr treats as a fatal error, producing a denial of service. The impact is limited to availability; the malformed value is consumed only as a divisor.

The fix rejects a zero s_blocks_per_group or s_inodes_per_group in the superblock validator, returning -EINVAL so the mount fails before any block-group or inode I/O occurs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7007.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-wrf2-79mm-cvw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-7007
- https://github.com/zephyrproject-rtos/zephyr/commit/babc0900ed40e6c023ccc26aa1a321f9388b66af
- https://github.com/zephyrproject-rtos/zephyr
