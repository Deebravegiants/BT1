# [M] ceph: fix memory leak in ceph_readdir when note_last_dentry returns error

## Summary
Severity: Medium
Advisory: CVE-2022-49107
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49107
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: fix memory leak in ceph_readdir when note_last_dentry returns error

Reset the last_readdir at the same time, and add a comment explaining
why we don't free last_readdir when dir_emit returns false.

## References
- https://git.kernel.org/stable/c/2fe82d3254029ef9ec4e7be890125d5ef4f537de
- https://git.kernel.org/stable/c/7f740ede35132d3d5d19747cad56a511d21bb156
- https://git.kernel.org/stable/c/e792575b902a3939ca482491ee9fb3a236f99640
- https://git.kernel.org/stable/c/f4429786129648a8f4bb1e5faa143c4478cc5c4a
- https://git.kernel.org/stable/c/f639d9867eea647005dc824e0e24f39ffc50d4e4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49107.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49107
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
