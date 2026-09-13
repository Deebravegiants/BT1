# [C] z2d OOB composition could lead to invalid memory access and corruption

## Summary
Severity: Critical
Advisory: CVE-2025-46333
Aliases: GHSA-mm4c-p35v-7hx3
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-04-25
Source: https://osv.dev/vulnerability/CVE-2025-46333
Type: osv

## Details
z2d is a pure Zig 2D graphics library. Versions of z2d after `0.5.1` and up to and including `0.6.0`, when writing from one surface to another using `z2d.compositor.StrideCompositor.run`, and higher-level operations when the anti-aliasing mode is set to `.default` (such as `Context.fill`, `Context.stroke`, `painter.fill`, and `painter.stroke`), the source surface can be completely out-of-bounds on the x-axis, but not on the y-axis, by way of a negative offset. This results in an overflow of the value controlling the length of the stride. In non-safe optimization modes (consumers compiling with `ReleaseFast` or `ReleaseSmall`), this could potentially lead to invalid memory accesses or corruption.

This issue is patched in version `0.6.1`. Users on an untagged version after `v0.5.1` and before `v0.6.1` are advised to update to address the vulnerability. Those still on Zig `0.13.0` are recommended to downgrade to `v0.5.1`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46333.json
- https://github.com/vancluever/z2d/security/advisories/GHSA-mm4c-p35v-7hx3
- https://nvd.nist.gov/vuln/detail/CVE-2025-46333
- https://github.com/vancluever/z2d/issues/104
- https://github.com/vancluever/z2d/issues/105
