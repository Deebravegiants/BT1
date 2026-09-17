# [M] ImageMagick: heap-buffer overflow in log colorspace handling

## Summary
Severity: Medium
Advisory: CVE-2025-55005
Aliases: GHSA-v393-38qx-v8fp
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-08-13
Source: https://osv.dev/vulnerability/CVE-2025-55005
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to version 7.1.2-1, when preparing to transform from Log to sRGB colorspaces, the logmap construction fails to handle cases where the reference-black or reference-white value is larger than 1024. This leads to corrupting memory beyond the end of the allocated logmap buffer. This issue has been patched in version 7.1.2-1.

## References
- https://goo.gle/bigsleep
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55005.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-v393-38qx-v8fp
- https://nvd.nist.gov/vuln/detail/CVE-2025-55005
