# [M] net: marvell: prestera: fix memory leak in prestera_rxtx_switch_init()

## Summary
Severity: Medium
Advisory: CVE-2022-49857
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49857
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.155, >=5.11.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: marvell: prestera: fix memory leak in prestera_rxtx_switch_init()

When prestera_sdma_switch_init() failed, the memory pointed to by
sw->rxtx isn't released. Fix it. Only be compiled, not be tested.

## References
- https://git.kernel.org/stable/c/31e5084ac6876e52dbb0a1cc4fc18b6c79979f31
- https://git.kernel.org/stable/c/409731df6310a33f4d0a3ef594d2410cdcd637f2
- https://git.kernel.org/stable/c/519b58bbfa825f042fcf80261cc18e1e35f85ffd
- https://git.kernel.org/stable/c/5333cf1b7f6861912aff6263978d4781f9858e47
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49857.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49857
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
