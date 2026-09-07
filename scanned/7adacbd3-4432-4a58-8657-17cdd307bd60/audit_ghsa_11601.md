# [H] Uncontrolled memory allocation via crafted SVG dimensions in @dicebear/converter

## Summary
Severity: High
Advisory: GHSA-v3r3-4qgc-vw66
CVE: CVE-2026-29112
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-v3r3-4qgc-vw66
Type: github-advisory

## Affected
- npm: `@dicebear/converter` — affected >=0 <9.4.0

## Details
### Impact

The `ensureSize()` function in `@dicebear/converter` (versions < 9.4.0) read the `width` and `height` attributes from the input SVG to determine the output canvas size for rasterization (PNG, JPEG, WebP, AVIF). An attacker who can supply a crafted SVG with extremely large dimensions (e.g. `width="999999999"`) could force the server to allocate excessive memory, leading to denial of service.

This primarily affects server-side applications that pass **untrusted or user-supplied SVGs** to the converter's `toPng()`, `toJpeg()`, `toWebp()`, or `toAvif()` functions. Applications that only convert self-generated DiceBear avatars are not practically exploitable, but are still recommended to upgrade.

### Patches

Fixed in version **9.4.0**. The `ensureSize()` function no longer reads SVG attributes to determine output size. Instead, a new `size` option (default: 512, max: 2048) controls the output dimensions. Invalid values (NaN, negative, zero, Infinity) fall back to the default.

### Workarounds

If upgrading is not immediately possible, validate and sanitize the `width` and `height` attributes of any untrusted SVG input before passing it to the converter.

## References
- https://github.com/dicebear/dicebear/security/advisories/GHSA-v3r3-4qgc-vw66
- https://nvd.nist.gov/vuln/detail/CVE-2026-29112
- https://github.com/dicebear/dicebear/commit/42a59eac46a3c68598859e608ec45e578b27614a
- https://github.com/dicebear/dicebear
- https://github.com/dicebear/dicebear/releases/tag/v9.4.0
