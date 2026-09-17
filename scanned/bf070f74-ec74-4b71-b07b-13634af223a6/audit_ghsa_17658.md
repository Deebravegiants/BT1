# [M] Electron vulnerable to Heap Buffer Overflow in NativeImage

## Summary
Severity: Medium
Advisory: GHSA-6r2x-8pq8-9489
CVE: CVE-2024-46993
CWE: CWE-122
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-06-30
Source: https://github.com/advisories/GHSA-6r2x-8pq8-9489
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <28.3.2
- npm: `electron` — affected >=29.0.0-alpha.1 <29.3.3
- npm: `electron` — affected >=30.0.0-alpha.1 <30.0.3

## Details
### Impact
The `nativeImage.createFromPath()` and `nativeImage.createFromBuffer()` functions call a function downstream that is vulnerable to a heap buffer overflow. An Electron program that uses either of the affected functions is vulnerable to a buffer overflow if an attacker is in control of the image's height, width, and contents.

### Workaround
There are no app-side workarounds for this issue. You must update your Electron version to be protected.

### Patches

- `v28.3.2`
- `v29.3.3`
- `v30.0.3`

### For More Information

If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org).

## References
- https://github.com/electron/electron/security/advisories/GHSA-6r2x-8pq8-9489
- https://nvd.nist.gov/vuln/detail/CVE-2024-46993
- https://github.com/electron/electron
