# [M] JLSEC-2026-894

## Summary
Severity: Medium
Advisory: JLSEC-2026-894
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-894
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+3

## Details
A heap-buffer-overflow flaw was found in ImageMagick’s PushShortPixel() function of quantum-private.h file. This vulnerability is triggered when an attacker passes a specially crafted TIFF image file to ImageMagick for conversion, potentially leading to a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2022-1115
- https://access.redhat.com/security/cve/CVE-2022-1115
- https://bugzilla.redhat.com/show_bug.cgi?id=2067022
- https://bugzilla.redhat.com/show_bug.cgi?id=2067022
- https://github.com/ImageMagick/ImageMagick/commit/c8718305f120293d8bf13724f12eed885d830b09
- https://github.com/ImageMagick/ImageMagick/commit/c8718305f120293d8bf13724f12eed885d830b09
- https://github.com/ImageMagick/ImageMagick/issues/4974
- https://github.com/ImageMagick/ImageMagick/issues/4974
- https://github.com/ImageMagick/ImageMagick6/commit/1f860f52bd8d58737ad883072203391096b30b51
- https://github.com/ImageMagick/ImageMagick6/commit/1f860f52bd8d58737ad883072203391096b30b51
