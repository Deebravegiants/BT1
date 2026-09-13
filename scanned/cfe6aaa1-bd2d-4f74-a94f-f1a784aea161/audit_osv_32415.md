# [C] libvips has a potential heap-based buffer overflow when attempting to convert multiband TIFF input to HEIF output

## Summary
Severity: Critical
Advisory: CVE-2025-29769
Aliases: GHSA-f8r8-43hh-rghm
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-04-07
Source: https://osv.dev/vulnerability/CVE-2025-29769
Type: osv

## Details
libvips is a demand-driven, horizontally threaded image processing library.  The heifsave operation could incorrectly determine the presence of an alpha channel in an input when it was not possible to determine the colour interpretation, known internally within libvips as "multiband". There aren't many ways to create a "multiband" input, but it is possible with a well-crafted TIFF image. If a "multiband" TIFF input image had 4 channels and HEIF-based output was requested, this led to libvips creating a 3 channel HEIF image without an alpha channel but then attempting to write 4 channels of data. This caused a heap buffer overflow, which could crash the process. This vulnerability is fixed in 8.16.1.

## References
- https://issues.oss-fuzz.com/issues/396460413
- https://lists.debian.org/debian-lts-announce/2025/04/msg00044.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29769.json
- https://github.com/libvips/libvips/security/advisories/GHSA-f8r8-43hh-rghm
- https://nvd.nist.gov/vuln/detail/CVE-2025-29769
- https://github.com/libvips/libvips/commit/9ab6784f693de50b00fa535b9efbbe9d2cbf71f2
- https://github.com/libvips/libvips/pull/4392
- https://github.com/libvips/libvips/pull/4394
