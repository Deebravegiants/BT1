# [M] ImageMagick has a use-after-free/double-free risk in Options::fontFamily when clearing family

## Summary
Severity: Medium
Advisory: CVE-2025-65955
Aliases: GHSA-q3hc-j9x5-mp9m
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-12-02
Source: https://osv.dev/vulnerability/CVE-2025-65955
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to 7.1.2-9 and 6.9.13-34, there is a vulnerability in ImageMagick’s Magick++ layer that manifests when Options::fontFamily is invoked with an empty string. Clearing a font family calls RelinquishMagickMemory on _drawInfo->font, freeing the font string but leaving _drawInfo->font pointing to freed memory while _drawInfo->family is set to that (now-invalid) pointer. Any later cleanup or reuse of _drawInfo->font re-frees or dereferences dangling memory. DestroyDrawInfo and other setters (Options::font, Image::font) assume _drawInfo->font remains valid, so destruction or subsequent updates trigger crashes or heap corruption. This vulnerability is fixed in 7.1.2-9 and 6.9.13-34.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65955.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-q3hc-j9x5-mp9m
- https://nvd.nist.gov/vuln/detail/CVE-2025-65955
- https://github.com/ImageMagick/ImageMagick/commit/6409f34d637a34a1c643632aa849371ec8b3b5a8
- https://github.com/ImageMagick/ImageMagick/commit/6f81eb15f822ad86e8255be75efad6f9762c32f8
