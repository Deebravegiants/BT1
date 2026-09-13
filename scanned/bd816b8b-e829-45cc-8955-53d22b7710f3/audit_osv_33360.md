# [H] ext4: avoid potential buffer over-read in parse_apply_sb_mount_options()

## Summary
Severity: High
Advisory: CVE-2025-40198
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40198
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <6.1.158, >=6.2.0 <6.6.114, >=6.7.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: avoid potential buffer over-read in parse_apply_sb_mount_options()

Unlike other strings in the ext4 superblock, we rely on tune2fs to
make sure s_mount_opts is NUL terminated.  Harden
parse_apply_sb_mount_options() by treating s_mount_opts as a potential
__nonstring.

## References
- https://git.kernel.org/stable/c/01829af7656b56d83682b3491265d583d502e502
- https://git.kernel.org/stable/c/2a0cf438320cdb783e0378570744c0ef0d83e934
- https://git.kernel.org/stable/c/7bf46ff83a0ef11836e38ebd72cdc5107209342d
- https://git.kernel.org/stable/c/8ecb790ea8c3fc69e77bace57f14cf0d7c177bd8
- https://git.kernel.org/stable/c/a6e94557cd05adc82fae0400f6e17745563e5412
- https://git.kernel.org/stable/c/b2bac84fde28fb6a88817b8b761abda17a1d300b
- https://git.kernel.org/stable/c/e651294218d2684302ee5ed95ccf381646f3e5b4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40198.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40198
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
