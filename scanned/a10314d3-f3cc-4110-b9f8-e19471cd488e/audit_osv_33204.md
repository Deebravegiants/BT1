# [H] fuse: Block access to folio overlimit

## Summary
Severity: High
Advisory: CVE-2025-39888
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39888
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

fuse: Block access to folio overlimit

syz reported a slab-out-of-bounds Write in fuse_dev_do_write.

When the number of bytes to be retrieved is truncated to the upper limit
by fc->max_pages and there is an offset, the oob is triggered.

Add a loop termination condition to prevent overruns.

## References
- https://git.kernel.org/stable/c/623719227b114d73a2cee45f1b343ced63ce09ec
- https://git.kernel.org/stable/c/9d81ba6d49a7457784f0b6a71046818b86ec7e44
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39888.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39888
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
