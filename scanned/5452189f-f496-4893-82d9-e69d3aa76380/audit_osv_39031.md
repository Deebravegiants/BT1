# [H] nsfs: tighten permission checks for ns iteration ioctls

## Summary
Severity: High
Advisory: CVE-2026-43403
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43403
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nsfs: tighten permission checks for ns iteration ioctls

Even privileged services should not necessarily be able to see other
privileged service's namespaces so they can't leak information to each
other. Use may_see_all_namespaces() helper that centralizes this policy
until the nstree adapts.

## References
- https://git.kernel.org/stable/c/0ad650e60150eda789deca5e78a6a09d26bf8fc9
- https://git.kernel.org/stable/c/2f3dea284c761c890d676f77d5e55c0c496b4ef4
- https://git.kernel.org/stable/c/3376b345df155ca36d8611857b41ff7d5183fc38
- https://git.kernel.org/stable/c/e6b899f08066e744f89df16ceb782e06868bd148
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43403.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43403
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
