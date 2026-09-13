# [M] JLSEC-2026-851

## Summary
Severity: Medium
Advisory: JLSEC-2026-851
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-851
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
There are several memory leaks in the MIFF coder in `/coders/miff.c` due to improper image depth values, which can be triggered by a specially crafted input file. These leaks could potentially lead to an impact to application availability or cause a denial of service. It was originally reported that the issues were in `AcquireMagickMemory()` because that is where LeakSanitizer detected the leaks, but the patch resolves issues in the MIFF coder, which incorrectly handles data being passed to `AcquireMagickMemory()`. This flaw affects ImageMagick versions prior to 7.0.9-0.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1894229
- https://bugzilla.redhat.com/show_bug.cgi?id=1894229
