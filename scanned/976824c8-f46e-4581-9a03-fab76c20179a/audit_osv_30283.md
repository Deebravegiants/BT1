# [M] dm: fix a crash if blk_alloc_disk fails

## Summary
Severity: Medium
Advisory: CVE-2024-50277
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50277
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm: fix a crash if blk_alloc_disk fails

If blk_alloc_disk fails, the variable md->disk is set to an error value.
cleanup_mapped_device will see that md->disk is non-NULL and it will
attempt to access it, causing a crash on this statement
"md->disk->private_data = NULL;".

## References
- https://git.kernel.org/stable/c/d7aec2a06730b774a97caaf48cbbc58330a85829
- https://git.kernel.org/stable/c/fed13a5478680614ba97fc87e71f16e2e197912e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50277.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50277
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
