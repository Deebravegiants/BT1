# [H] ceph: fix cred leak in ceph_mds_check_access()

## Summary
Severity: High
Advisory: CVE-2024-56563
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56563
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: fix cred leak in ceph_mds_check_access()

get_current_cred() increments the reference counter, but the
put_cred() call was missing.

## References
- https://git.kernel.org/stable/c/c5cf420303256dcd6ff175643e9e9558543c2047
- https://git.kernel.org/stable/c/e3d1c9e2b811f13bdbbb962c2b17a6091c28522c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56563.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56563
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
