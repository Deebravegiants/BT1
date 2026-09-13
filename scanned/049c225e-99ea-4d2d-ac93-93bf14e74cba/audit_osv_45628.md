# [M] JLSEC-2026-142

## Summary
Severity: Medium
Advisory: JLSEC-2026-142
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-142
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.4.4+0 <3.4.9+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From 3.4.0 to before 3.4.9, a missing bounds check on the dataWindow attribute in EXR file headers allows an attacker to trigger a signed integer overflow in `generic_unpack()`. By setting dataWindow.min.x to a large negative value, OpenEXRCore computes an enormous image width, which is later used in a signed integer multiplication that overflows, causing the process to terminate with SIGILL via UBSan. This vulnerability is fixed in 3.4.9.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.9
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-v76p-4qvv-vh4g
