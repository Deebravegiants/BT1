# [M] pinctrl: renesas: core: Fix possible null-ptr-deref in sh_pfc_map_resources()

## Summary
Severity: Medium
Advisory: CVE-2022-49445
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49445
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: renesas: core: Fix possible null-ptr-deref in sh_pfc_map_resources()

It will cause null-ptr-deref when using 'res', if platform_get_resource()
returns NULL, so move using 'res' after devm_ioremap_resource() that
will check it to avoid null-ptr-deref.
And use devm_platform_get_and_ioremap_resource() to simplify code.

## References
- https://git.kernel.org/stable/c/5376e3d904532e657fd7ca1a9b1ff3d351527b90
- https://git.kernel.org/stable/c/5ed0519d425619b435150372cce2ffeec71581fa
- https://git.kernel.org/stable/c/e3a1ad8fd0ac11f4fa1260c23b5db71a25473254
- https://git.kernel.org/stable/c/f991879762392c19661af5b722578089a12b305f
- https://git.kernel.org/stable/c/fb4f022b3ad1f3ff3cafdbc7d51896090ae17701
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49445.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49445
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
