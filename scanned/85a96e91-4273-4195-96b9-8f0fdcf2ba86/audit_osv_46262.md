# [H] JLSEC-2026-893

## Summary
Severity: High
Advisory: JLSEC-2026-893
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-893
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+3

## Details
A heap-use-after-free flaw was found in ImageMagick's RelinquishDCMInfo() function of dcm.c file. This vulnerability is triggered when an attacker passes a specially crafted DICOM image file to ImageMagick for conversion, potentially leading to information disclosure and a denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2064538
- https://bugzilla.redhat.com/show_bug.cgi?id=2064538
