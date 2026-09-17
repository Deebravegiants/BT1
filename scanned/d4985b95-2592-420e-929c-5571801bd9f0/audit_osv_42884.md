# [H] dm_early_create: fix freeing used table on dm_resume failure

## Summary
Severity: High
Advisory: CVE-2026-72102
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72102
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm_early_create: fix freeing used table on dm_resume failure

If dm_resume fails, the kernel attempts to free table with
dm_table_destroy, but the table was already instantiated with
dm_swap_table. This commit skips the call to dm_table_destroy in this
case.

## References
- https://git.kernel.org/stable/c/259ce9e3fc3a3f8c4e393a2072b8f34302eb4d5a
- https://git.kernel.org/stable/c/366665416f20527ff7cad548a32d1ddf23195740
- https://git.kernel.org/stable/c/3ba377a47a093cc19647ca7f102acd33a211d472
- https://git.kernel.org/stable/c/5f6500d44a912d4aed664600966706d76b81d9af
- https://git.kernel.org/stable/c/72c3283a2abd60ecef295e02270f22ef1dfccd25
- https://git.kernel.org/stable/c/7d8ed7cb844df21e4d93af11250fb3a5cb861147
- https://git.kernel.org/stable/c/92e3c93d60be1f2425738cd66dbadac7d6bc0cd1
- https://git.kernel.org/stable/c/d6066145347e14db84c35b445e309f095d0d8125
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72102.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72102
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
