# [H] nsfs: tighten permission checks for handle opening

## Summary
Severity: High
Advisory: CVE-2026-43391
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43391
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.50, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nsfs: tighten permission checks for handle opening

Even privileged services should not necessarily be able to see other
privileged service's namespaces so they can't leak information to each
other. Use may_see_all_namespaces() helper that centralizes this policy
until the nstree adapts.

## References
- https://git.kernel.org/stable/c/1797ee11451f1b2be69863a9f5bd43b948813fdf
- https://git.kernel.org/stable/c/24ebaf6676ae4f74f4856eb645959b15e62bc1b4
- https://git.kernel.org/stable/c/d2324a9317f00013facb0ba00b00440e19d2af5e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43391.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43391
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
