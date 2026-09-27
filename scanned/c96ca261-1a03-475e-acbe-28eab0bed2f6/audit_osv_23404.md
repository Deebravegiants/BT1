# [M] drm/amd/display: fix memory leak when using debugfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2022-48698
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2022-48698
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.68, >=5.16.0 <5.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: fix memory leak when using debugfs_lookup()

When calling debugfs_lookup() the result must have dput() called on it,
otherwise the memory will leak over time.  Fix this up by properly
calling dput().

## References
- https://git.kernel.org/stable/c/3a6279d243cb035eaaff1450980b40cf19748f05
- https://git.kernel.org/stable/c/58acd2ebae034db3bacf38708f508fbd12ae2e54
- https://git.kernel.org/stable/c/cbfac7fa491651c57926c99edeb7495c6c1aeac2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48698.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48698
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
