# [H] powercap: intel_rapl: Fix off by one in get_rpi()

## Summary
Severity: High
Advisory: CVE-2024-49862
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49862
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

powercap: intel_rapl: Fix off by one in get_rpi()

The rp->priv->rpi array is either rpi_msr or rpi_tpmi which have
NR_RAPL_PRIMITIVES number of elements.  Thus the > needs to be >=
to prevent an off by one access.

## References
- https://git.kernel.org/stable/c/288cbc505e2046638c615c36357cb78bc9fee1e0
- https://git.kernel.org/stable/c/6a34f3b0d7f11fb6ed72da315fd2360abd9c0737
- https://git.kernel.org/stable/c/851e7f7f14a15f4e47b7d0f70d5c4a2b95b824d6
- https://git.kernel.org/stable/c/95f6580352a7225e619551febb83595bcb77ab17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49862.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49862
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
