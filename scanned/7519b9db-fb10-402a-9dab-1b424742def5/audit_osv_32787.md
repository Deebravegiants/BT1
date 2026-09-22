# [H] smb: client: Avoid race in open_cached_dir with lease breaks

## Summary
Severity: High
Advisory: CVE-2025-37954
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37954
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.91, >=6.7.0 <6.12.29, >=6.13.0 <6.14.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: Avoid race in open_cached_dir with lease breaks

A pre-existing valid cfid returned from find_or_create_cached_dir might
race with a lease break, meaning open_cached_dir doesn't consider it
valid, and thinks it's newly-constructed. This leaks a dentry reference
if the allocation occurs before the queued lease break work runs.

Avoid the race by extending holding the cfid_list_lock across
find_or_create_cached_dir and when the result is checked.

## References
- https://git.kernel.org/stable/c/2407265dc32bc8cc45b62a612c2a214ba9038e8b
- https://git.kernel.org/stable/c/2ed98e89ebc2e1bc73534dc3c18cb7843a889ff9
- https://git.kernel.org/stable/c/3ca02e63edccb78ef3659bebc68579c7224a6ca2
- https://git.kernel.org/stable/c/571dcf3d27b24800c171aea7b5e04ff06d10e2e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37954.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37954
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
