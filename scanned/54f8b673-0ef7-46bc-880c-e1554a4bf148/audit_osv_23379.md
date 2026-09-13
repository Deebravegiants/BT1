# [M] cgroup: cgroup_get_from_id() must check the looked-up kn is a directory

## Summary
Severity: Medium
Advisory: CVE-2022-48638
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2022-48638
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.72, >=5.16.0 <5.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

cgroup: cgroup_get_from_id() must check the looked-up kn is a directory

cgroup has to be one kernfs dir, otherwise kernel panic is caused,
especially cgroup id is provide from userspace.

## References
- https://git.kernel.org/stable/c/1e9571887f97b17cf3ffe9aa4da89090ea60988b
- https://git.kernel.org/stable/c/8484a356cee8ce3d6a8e6266ff99be326e9273ad
- https://git.kernel.org/stable/c/df02452f3df069a59bc9e69c84435bf115cb6e37
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48638.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48638
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
