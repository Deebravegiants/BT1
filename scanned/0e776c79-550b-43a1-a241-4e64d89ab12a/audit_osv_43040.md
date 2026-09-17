# [C] netfs: Fix netfs_create_write_req() to handle async cache object creation

## Summary
Severity: Critical
Advisory: CVE-2026-72366
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72366
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix netfs_create_write_req() to handle async cache object creation

netfs_create_write_req() will skip caching if the fscache cookie is
disabled, but this is a problem because async cache object creation might
not have got far enough yet that has been enabled - thereby causing the
call to fscache_begin_write_operation() to be skipped.

Fix this by removing the checks on the cookie and delegating this to
fscache_begin_write_operation().

## References
- https://git.kernel.org/stable/c/1188a9846fadeacf9d1430b528e5217f749d665b
- https://git.kernel.org/stable/c/8ab75e445c161c4cb504aa98e20ce1dd1ecd8e9a
- https://git.kernel.org/stable/c/dbd6f56d975b23241b7bbb11bb8f562af548a0aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72366.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72366
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
