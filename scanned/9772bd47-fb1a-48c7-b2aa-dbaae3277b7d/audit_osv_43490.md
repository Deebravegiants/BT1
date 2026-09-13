# [H] bpf: Guard __get_user acesss with access_ok for uprobe_multi data

## Summary
Severity: High
Advisory: CVE-2026-74258
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74258
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Guard __get_user acesss with access_ok for uprobe_multi data

As reported by sashiko [1] we need to use access_ok to check the user
space data bounds before we use __get-user to get it.

[1] https://lore.kernel.org/bpf/20260610145235.CB1441F00893@smtp.kernel.org/

## References
- https://git.kernel.org/stable/c/4d87a251d45b4a95eb4c0abcfab809c9f231258a
- https://git.kernel.org/stable/c/c6d51ad36490013ee9df94a372d3bf794bd304d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74258.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74258
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
