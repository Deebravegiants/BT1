# [H] Arbitrary Code Execution in `AppImage` version `ImageMagick`

## Summary
Severity: High
Advisory: CVE-2024-41817
Aliases: GHSA-8rxc-922v-phg8
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41817
Type: osv

## Details
ImageMagick is a free and open-source software suite, used for editing and manipulating digital images. The `AppImage` version `ImageMagick` might use an empty path when setting `MAGICK_CONFIGURE_PATH` and `LD_LIBRARY_PATH` environment variables while executing, which might lead to arbitrary code execution by loading malicious configuration files or shared libraries in the current working directory while executing `ImageMagick`. The vulnerability is fixed in 7.11-36.

## References
- https://github.com/ImageMagick/ImageMagick/blob/3b22378a23d59d7517c43b65b1822f023df357a0/app-image/AppRun#L11-L14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41817.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-8rxc-922v-phg8
- https://nvd.nist.gov/vuln/detail/CVE-2024-41817
- https://github.com/ImageMagick/ImageMagick/commit/6526a2b28510ead6a3e14de711bb991ad9abff38
