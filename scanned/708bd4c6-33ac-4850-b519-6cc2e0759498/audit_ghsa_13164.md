# [H] @napi-rs/image affected by libwebp CVE

## Summary
Severity: High
Advisory: GHSA-4vjr-crvh-383h
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-27
Source: https://github.com/advisories/GHSA-4vjr-crvh-383h
Type: github-advisory

## Affected
- npm: `@napi-rs/image` — affected >=0 <1.7.0

## Details
### Impact
Heap buffer overflow in `libwebp` allows a remote attacker to perform an out of bounds memory write via a crafted webp image.

### References
- https://github.com/advisories/GHSA-j7hp-h8jx-5ppr
- https://blog.isosceles.com/the-webp-0day/

## References
- https://github.com/Brooooooklyn/Image/security/advisories/GHSA-4vjr-crvh-383h
- https://github.com/Brooooooklyn/Image/commit/aa07979f6cd0c534a8befea87fac1210a3b621c1
- https://blog.isosceles.com/the-webp-0day
- https://github.com/Brooooooklyn/Image
- https://github.com/Brooooooklyn/Image/releases/tag/%40napi-rs%2Fimage%401.7.0
- https://github.com/advisories/GHSA-j7hp-h8jx-5ppr
