# [H] f2fs: fix to avoid out-of-boundary access in devs.path

## Summary
Severity: High
Advisory: CVE-2025-38652
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38652
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to avoid out-of-boundary access in devs.path

- touch /mnt/f2fs/012345678901234567890123456789012345678901234567890123
- truncate -s $((1024*1024*1024)) \
  /mnt/f2fs/012345678901234567890123456789012345678901234567890123
- touch /mnt/f2fs/file
- truncate -s $((1024*1024*1024)) /mnt/f2fs/file
- mkfs.f2fs /mnt/f2fs/012345678901234567890123456789012345678901234567890123 \
  -c /mnt/f2fs/file
- mount /mnt/f2fs/012345678901234567890123456789012345678901234567890123 \
  /mnt/f2fs/loop

[16937.192225] F2FS-fs (loop0): Mount Device [ 0]: /mnt/f2fs/012345678901234567890123456789012345678901234567890123\xff\x01,      511,        0 -    3ffff
[16937.192268] F2FS-fs (loop0): Failed to find devices

If device path length equals to MAX_PATH_LEN, sbi->devs.path[] may
not end up w/ null character due to path array is fully filled, So
accidently, fields locate after path[] may be treated as part of
device path, result in parsing wrong device path.

struct f2fs_dev_info {
...
	char path[MAX_PATH_LEN];
...
};

Let's add one byte space for sbi->devs.path[] to store null
character of device path string.

## References
- https://git.kernel.org/stable/c/1b1efa5f0e878745e94a98022e8edc675a87d78e
- https://git.kernel.org/stable/c/1cf1ff15f262e8baf12201b270b6a79f9d119b2d
- https://git.kernel.org/stable/c/345fc8d1838f3f8be7c8ed08d86a13dedef67136
- https://git.kernel.org/stable/c/3466721f06edff834f99d9f49f23eabc6b2cb78e
- https://git.kernel.org/stable/c/5661998536af52848cc4d52a377e90368196edea
- https://git.kernel.org/stable/c/666b7cf6ac9aa074b8319a2b68cba7f2c30023f0
- https://git.kernel.org/stable/c/70849d33130a2cf1d6010069ed200669c8651fbd
- https://git.kernel.org/stable/c/755427093e4294ac111c3f9e40d53f681a0fbdaa
- https://git.kernel.org/stable/c/dc0172c74bd9edaee7bea2ebb35f3dbd37a8ae80
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38652.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38652
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
