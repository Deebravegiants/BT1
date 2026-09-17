# [M] fs/ntfs3: Additional check in ni_clear()

## Summary
Severity: Medium
Advisory: CVE-2024-50244
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50244
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Additional check in ni_clear()

Checking of NTFS_FLAGS_LOG_REPLAYING added to prevent access to
uninitialized bitmap during replay process.

## References
- https://git.kernel.org/stable/c/14a23e15a5e8331bb0cf21288723fa530a45b2a4
- https://git.kernel.org/stable/c/60fb94ef46c2359dd06cbe30bfc2499f639433df
- https://git.kernel.org/stable/c/7a4ace681dbb652aeb40e1b88f9134b880fdeeb5
- https://git.kernel.org/stable/c/80824967ec714dda02cd79091aa186bbc16c5cf3
- https://git.kernel.org/stable/c/d178944db36b3369b78a08ba520de109b89bf2a9
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50244.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50244
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
