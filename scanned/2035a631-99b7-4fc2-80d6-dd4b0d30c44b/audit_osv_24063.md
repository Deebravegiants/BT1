# [H] misc: fastrpc: fix memory corruption on probe

## Summary
Severity: High
Advisory: CVE-2022-49952
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49952
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.213, >=5.5.0 <5.10.142, >=5.11.0 <5.15.66, >=5.16.0 <5.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: fix memory corruption on probe

Add the missing sanity check on the probed-session count to avoid
corrupting memory beyond the fixed-size slab-allocated session array
when there are more than FASTRPC_MAX_SESSIONS sessions defined in the
devicetree.

## References
- https://git.kernel.org/stable/c/0e33b0f322fecd7a92d9dc186535cdf97940a856
- https://git.kernel.org/stable/c/9baa1415d9abdd1e08362ea2dcfadfacee8690b5
- https://git.kernel.org/stable/c/c0425c2facd9166fa083f90c9f3187ace0c7837a
- https://git.kernel.org/stable/c/c99bc901d5eb9fbdd7bd39f625e170ce97390336
- https://git.kernel.org/stable/c/ec186b9f4aa2e6444d5308a6cc268aada7007639
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49952.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49952
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
