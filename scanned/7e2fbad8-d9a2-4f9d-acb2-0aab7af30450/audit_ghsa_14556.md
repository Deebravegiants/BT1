# [M] Versionize::deserialize implementation for FamStructWrapper<T> is lacking bound checks, potentially leading to out of bounds memory accesses

## Summary
Severity: Medium
Advisory: GHSA-8vxc-r5wp-vgvc
CVE: CVE-2023-28448
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-8vxc-r5wp-vgvc
Type: github-advisory

## Affected
- crates.io: `versionize` — affected >=0.1.1 <0.1.10

## Details
### Impact

An issue was discovered in the `Versionize::deserialize` implementation provided by the `versionize` crate for `vmm_sys_util::fam::FamStructWrapper`, which can lead to out of bounds memory accesses.

### Patches

The impact started with version 0.1.1. The issue was corrected in version 0.1.10 by inserting a check that verifies, for any deserialized header, the lengths of compared flexible arrays are equal and aborting deserialization otherwise.

### Workarounds
\-

### References
- https://github.com/firecracker-microvm/versionize/pull/53

## References
- https://github.com/firecracker-microvm/versionize/security/advisories/GHSA-8vxc-r5wp-vgvc
- https://nvd.nist.gov/vuln/detail/CVE-2023-28448
- https://github.com/firecracker-microvm/versionize/pull/53
- https://github.com/firecracker-microvm/versionize/commit/a57a051ba006cfa3b41a0532f484df759e008d47
- https://github.com/firecracker-microvm/versionize
- https://github.com/firecracker-microvm/versionize/releases/tag/v0.1.10
- https://rustsec.org/advisories/RUSTSEC-2023-0030.html
