# [M] scsi: pm8001: Fix memory leak in pm8001_chip_fw_flash_update_req()

## Summary
Severity: Medium
Advisory: CVE-2022-49119
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49119
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: pm8001: Fix memory leak in pm8001_chip_fw_flash_update_req()

In pm8001_chip_fw_flash_update_build(), if
pm8001_chip_fw_flash_update_build() fails, the struct fw_control_ex
allocated must be freed.

## References
- https://git.kernel.org/stable/c/a25ed5f21f94f9ae4bcc8dd747e978668890c921
- https://git.kernel.org/stable/c/d83574666bac4b1462e90df393fbed6c5f57d1a3
- https://git.kernel.org/stable/c/e5ecdb01952f230921aa8163d8d7f4c97c925ed8
- https://git.kernel.org/stable/c/f792a3629f4c4aa4c3703d66b43ce1edcc3ec09a
- https://git.kernel.org/stable/c/fe5b8ea5583b5c3f6f68e06acba50387edf3b5d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49119.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49119
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
