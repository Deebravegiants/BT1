# [M] JLSEC-2026-844

## Summary
Severity: Medium
Advisory: JLSEC-2026-844
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-844
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
TIFFGetProfiles() in `/coders/tiff.c` calls strstr() which causes a large out-of-bounds read when it searches for `"dc:format=\"image/dng\"` within `profile` due to improper string handling, when a crafted input file is provided to ImageMagick. The patch uses a StringInfo type instead of a raw C string to remedy this. This could cause an impact to availability of the application. This flaw affects ImageMagick versions prior to 7.0.9-0.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1891613
- https://bugzilla.redhat.com/show_bug.cgi?id=1891613
