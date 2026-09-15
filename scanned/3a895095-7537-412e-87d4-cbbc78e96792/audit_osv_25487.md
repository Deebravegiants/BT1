# [M] Imagemagick: heap-buffer-overflow in pushcharpixel() in quantum-private.h

## Summary
Severity: Medium
Advisory: CVE-2023-3745
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-3745
Type: osv

## Details
A heap-based buffer overflow issue was found in ImageMagick's PushCharPixel() function in quantum-private.h. This issue may allow a local attacker to trick the user into opening a specially crafted file, triggering an out-of-bounds read error and allowing an application to crash, resulting in a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2023-3745
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3745.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3745
- https://bugzilla.redhat.com/show_bug.cgi?id=2223557
- https://github.com/ImageMagick/ImageMagick/issues/1857
- https://github.com/ImageMagick/ImageMagick/commit/54cdc146bbe50018526770be201b56643ad58ba7
- https://github.com/ImageMagick/ImageMagick/commit/651672f19c75161a6159d9b6838fd3095b6c5304
- https://github.com/ImageMagick/ImageMagick6/commit/7486477aa00c5c7856b111506da075b6cdfa8b73
- https://github.com/ImageMagick/ImageMagick6/commit/b466a96965afc1308a4ace93f5535c2b770f294b
