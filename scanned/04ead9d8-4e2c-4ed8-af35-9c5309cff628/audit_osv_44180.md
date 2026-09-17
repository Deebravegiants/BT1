# [H] s390/vfio_ccw: Ensure index for read/write regions are within range

## Summary
Severity: High
Advisory: CVE-2026-80552
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80552
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.15.218, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/vfio_ccw: Ensure index for read/write regions are within range

The introduction of the capability chain rightly clamped the
region indexes to the range of the capabilities itself, but
neglected to do so for the existing read/write regions which
should also be enforced.

## References
- https://git.kernel.org/stable/c/3acbedf5c0b8e0971f0de423c05cc02bbf6ddb99
- https://git.kernel.org/stable/c/649badf3a2fd8929e40198603a2cb21b74c21700
- https://git.kernel.org/stable/c/79ea5e0c4c8a9842ae85f45062d947b3297dfc07
- https://git.kernel.org/stable/c/988d9b5be3c2c4baf9457ce8e11b477e13eb9fcf
- https://git.kernel.org/stable/c/9f5f9a78fedc45bc29d6a0a64e3a3472361afae5
- https://git.kernel.org/stable/c/d3b1e38404b22df5a1f93019f2bb656feaad5ae3
- https://git.kernel.org/stable/c/d597fa1273802941c7801202135976fecc29672b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80552.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80552
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
