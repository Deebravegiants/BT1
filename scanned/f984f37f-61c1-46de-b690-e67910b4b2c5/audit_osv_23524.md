# [M] net/smc: Fix NULL pointer dereference in smc_pnet_find_ib()

## Summary
Severity: Medium
Advisory: CVE-2022-49060
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49060
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.190, >=5.5.0 <5.10.112, >=5.11.0 <5.15.35, >=5.16.0 <5.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: Fix NULL pointer dereference in smc_pnet_find_ib()

dev_name() was called with dev.parent as argument but without to
NULL-check it before.
Solve this by checking the pointer before the call to dev_name().

## References
- https://git.kernel.org/stable/c/22025513ced3d599ee8b24169141c95cf2467a4a
- https://git.kernel.org/stable/c/35b91e49bc80ca944a8679c3b139ddaf2f8eea0f
- https://git.kernel.org/stable/c/3a523807f01455fe9a0c1a433f27cd4411ee400f
- https://git.kernel.org/stable/c/a05f5e26cb8bb4d07e0595545fcad1bb406f0085
- https://git.kernel.org/stable/c/d22f4f977236f97e01255a80bca2ea93a8094fc8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49060.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49060
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
