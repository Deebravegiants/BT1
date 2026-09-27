# [M] JLSEC-2026-908

## Summary
Severity: Medium
Advisory: JLSEC-2026-908
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-908
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.1+1

## Details
A heap-based buffer overflow vulnerability was found  in `coders/tiff.c` in ImageMagick. This issue may allow a local attacker to trick the user into opening a specially crafted file, resulting in an application crash and denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-3428
- https://access.redhat.com/security/cve/CVE-2023-3428
- https://bugzilla.redhat.com/show_bug.cgi?id=2218369
- https://bugzilla.redhat.com/show_bug.cgi?id=2218369
