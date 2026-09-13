# [H] netfs: Fix overrun check in netfs_extract_user_iter()

## Summary
Severity: High
Advisory: CVE-2026-64217
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64217
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix overrun check in netfs_extract_user_iter()

Fix netfs_extract_user_iter() so that if iov_iter_extract_pages() overfills
pages[], then those pages don't get included in the iterator constructed at
the end of the function.  If there was an overfill, memory corruption has
already happened.

## References
- https://git.kernel.org/stable/c/00efe58bbdcc93272d579ca24bfc912563f4a204
- https://git.kernel.org/stable/c/0ef37eef83fad3542ee06db2940433ae1a92b39d
- https://git.kernel.org/stable/c/96cc3beb2390ba9f9c128c5733c0ccfe450dd4f9
- https://git.kernel.org/stable/c/afeb32d9bf9aaeea51d0f723a19f14afb73bd94d
- https://git.kernel.org/stable/c/f48b9157f0f611fa436c360648603d5ded719b12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64217.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64217
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
