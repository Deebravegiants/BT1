# [H] ExifReader is vulnerable to denial of service via crafted ICC `mluc` tag

## Summary
Severity: High
Advisory: GHSA-h64w-w9pr-82m4
CVE: CVE-2026-8813
CWE: CWE-1284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-h64w-w9pr-82m4
Type: github-advisory

## Affected
- npm: `exifreader` — affected >=2.10.0 <4.39.0

## Details
### Impact

When parsing an image with an embedded ICC profile that contains a crafted `multiLocalizedUnicodeType` (`mluc`) tag, ExifReader can be made to allocate memory proportional to attacker-controlled fields in the tag rather than to
the actual size of the input. Processing such an image causes excessive memory consumption and can terminate the host process (out-of-memory).

Any application that calls `ExifReader.load()` on untrusted images, for example, user uploads in a web service, is affected. ICC profiles are carried in JPEG, TIFF, PNG, HEIC, AVIF, JPEG XL, and WebP, so the issue is reachable from any of those formats.

### Patches

Fixed in `exifreader@4.39.0`. Upgrade with:

    npm install exifreader@latest

Bower users consume the bundled `dist/` files from this repository, and the same fix is committed there.

### Workarounds

If upgrading is not immediately possible, configure a [custom build](https://github.com/mattiasw/ExifReader#configure-a-custom-build) that excludes the `icc` module so that ICC parsing (and therefore this code path) is skipped entirely.

### Resources

- Patch: https://github.com/mattiasw/ExifReader/commit/c9d88b67e127b2dcc7b46e328df468257fb2dc30

## References
- https://github.com/mattiasw/ExifReader/security/advisories/GHSA-h64w-w9pr-82m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-8813
- https://github.com/mattiasw/ExifReader/commit/c9d88b67e127b2dcc7b46e328df468257fb2dc30
- https://github.com/mattiasw/ExifReader
- https://security.snyk.io/vuln/SNYK-JS-EXIFREADER-16689335
