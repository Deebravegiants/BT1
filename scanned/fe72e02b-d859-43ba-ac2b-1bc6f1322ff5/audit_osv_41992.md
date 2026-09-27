# [H] i2c: core: fix adapter deregistration race

## Summary
Severity: High
Advisory: CVE-2026-64279
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64279
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: core: fix adapter deregistration race

Adapters can be looked up by their id using i2c_get_adapter() which
takes a reference to the embedded struct device.

Remove the adapter from the IDR before tearing it down during
deregistration (and on registration failure) to make sure its resources
are not accessed after having been freed (e.g. the device name).

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/11dfa37bf544cc806f21742ca2fd2d841bd7032e
- https://git.kernel.org/stable/c/35dbd1f1f603401155cbd3a180bb18e3a3b675b8
- https://git.kernel.org/stable/c/9882a9bd74db08e7bae5821a7050627ae92d3380
- https://git.kernel.org/stable/c/b1a58ed9eab146b36f41a55db8f5d7ce9fdedf3f
- https://git.kernel.org/stable/c/b6d2af6fe9c1f5ec0484536753c979cbd40a8ac3
- https://git.kernel.org/stable/c/bb234487a447a99315add1b46aa57b72e163e1eb
- https://git.kernel.org/stable/c/d39282f552dd6c35b9b84b4af78f1198c24f3373
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64279.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64279
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
