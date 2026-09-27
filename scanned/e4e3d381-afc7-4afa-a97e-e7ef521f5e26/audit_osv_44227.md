# [H] apparmor: fix potential UAF in aa_replace_profiles

## Summary
Severity: High
Advisory: CVE-2026-80619
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80619
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: fix potential UAF in aa_replace_profiles

The function aa_replace_profiles was accessing udata->size after calling
aa_put_loaddata(udata), causing a potential UAF.

Fixed this by saving the size to a local variable before dropping the
reference.

## References
- https://git.kernel.org/stable/c/57b1bd4486d56254bb8af1a8f3d4445bbe505290
- https://git.kernel.org/stable/c/5cba148eae6e8550c2889f5c0f94d72bed864321
- https://git.kernel.org/stable/c/7b42f95813dc9ceb6bda35afcf914630909a19f9
- https://git.kernel.org/stable/c/9d37dc6376e336dc4b4f39a7ad0d069aa70e9495
- https://git.kernel.org/stable/c/9d8e47cbce7536f19c96e37d0685a042010187ee
- https://git.kernel.org/stable/c/c0f3a3fda617beeec58708720304dd026a1a4dd7
- https://git.kernel.org/stable/c/c44de0880b7ccc15c70a6352b5e107677d32b061
- https://git.kernel.org/stable/c/dd5f1202f45a2dbe2c7dd10093f5c6bb2d8ac5bb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80619.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80619
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
