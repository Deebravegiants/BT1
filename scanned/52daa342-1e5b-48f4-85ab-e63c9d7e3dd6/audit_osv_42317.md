# [H] Gimp: out-of-bounds read in file-icns plugin causes information disclosure or crash on crafted icns images

## Summary
Severity: High
Advisory: CVE-2026-66759
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-66759
Type: osv

## Details
A flaw was found in the file-icns plugin in GIMP. When applying a decompressed mask during ICNS image processing, the plugin reads from the mask data buffer without verifying if the cursor exceeds the allocated resource size. If a crafted file contains a truncated mask resource, the icns_decompress function continues reading past the bounds of the buffer. This out-of-bounds read vulnerability results in information disclosure of heap contents, where memory contents are leaked as alpha channel pixel values, or a crash leading to a denial of service if unmapped memory is accessed.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:50817
- https://access.redhat.com/security/cve/CVE-2026-66759
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66759.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66759
- https://bugzilla.redhat.com/show_bug.cgi?id=2507557
- https://gitlab.gnome.org/GNOME/gimp/-/issues/16528
- https://gitlab.gnome.org/GNOME/gimp
