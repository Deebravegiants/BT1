# [H] sharp vulnerability in libwebp dependency CVE-2023-4863

## Summary
Severity: High
Advisory: GHSA-54xq-cgqr-rpm3
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-54xq-cgqr-rpm3
Type: github-advisory

## Affected
- npm: `sharp` — affected >=0 <0.32.6

## Details
## Overview

sharp uses libwebp to decode WebP images and versions prior to the latest 0.32.6 are vulnerable to the high severity https://github.com/advisories/GHSA-j7hp-h8jx-5ppr.

## Who does this affect?

Almost anyone processing untrusted input with versions of sharp prior to 0.32.6.

## How to resolve this?

### Using prebuilt binaries provided by sharp?

Most people rely on the prebuilt binaries provided by sharp.

Please upgrade sharp to the latest 0.32.6, which provides libwebp 1.3.2.

### Using a globally-installed libvips?

Please ensure you are using the latest libwebp 1.3.2.

## Possible workaround

Add the following to your code to prevent sharp from decoding WebP images.
```js
sharp.block({ operation: ["VipsForeignLoadWebp"] });
```

## References
- https://github.com/lovell/sharp/security/advisories/GHSA-54xq-cgqr-rpm3
- https://github.com/lovell/sharp/commit/dbce6fab795ca4250bda9b1ef502c1fdb7d4a30c
- https://github.com/lovell/sharp
