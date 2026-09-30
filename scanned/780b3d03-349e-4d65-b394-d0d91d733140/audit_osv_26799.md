# [H] ice: fix wrong fallback logic for FDIR

## Summary
Severity: High
Advisory: CVE-2023-54040
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54040
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.107, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix wrong fallback logic for FDIR

When adding a FDIR filter, if ice_vc_fdir_set_irq_ctx returns failure,
the inserted fdir entry will not be removed and if ice_vc_fdir_write_fltr
returns failure, the fdir context info for irq handler will not be cleared
which may lead to inconsistent or memory leak issue. This patch refines
failure cases to resolve this issue.

## References
- https://git.kernel.org/stable/c/391d28c0e38c0e5b11a4240a2b4976cf63e87f45
- https://git.kernel.org/stable/c/aad3b871efe26f36f45f8b4649653b5d3fd9c35e
- https://git.kernel.org/stable/c/b4a01ace20f5c93c724abffc0a83ec84f514b98d
- https://git.kernel.org/stable/c/cbfed5f114b5310f221979fc8190f55c6abc3400
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54040.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54040
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
