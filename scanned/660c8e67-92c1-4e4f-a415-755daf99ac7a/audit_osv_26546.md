# [M] caif: fix memory leak in cfctrl_linkup_request()

## Summary
Severity: Medium
Advisory: CVE-2023-53330
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53330
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.19, >=6.1.0 <6.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

caif: fix memory leak in cfctrl_linkup_request()

When linktype is unknown or kzalloc failed in cfctrl_linkup_request(),
pkt is not released. Add release process to error path.

## References
- https://git.kernel.org/stable/c/1dddeceb26002cfea4c375e92ac6498768dc7349
- https://git.kernel.org/stable/c/33df9c5d5e2a18c70f5f5f3c2757d654c1b6ffa3
- https://git.kernel.org/stable/c/3acf3783a84cbdf0c9f8cf2f32ee9c49af93a2da
- https://git.kernel.org/stable/c/3ad47c8aa5648226184415e4a0cb1bf67ffbfd48
- https://git.kernel.org/stable/c/84b2cc7b36b7f6957d307fb3d01603f93cb2d655
- https://git.kernel.org/stable/c/badea57569db04b010e922e29a7aaf40a979a70b
- https://git.kernel.org/stable/c/dc1bc903970bdf63ca40ab923d3ccb765da9a8d9
- https://git.kernel.org/stable/c/fe69230f05897b3de758427b574fc98025dfc907
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53330.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53330
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
