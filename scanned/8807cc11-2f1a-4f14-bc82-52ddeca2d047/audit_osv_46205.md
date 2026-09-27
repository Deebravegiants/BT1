# [C] A malicious EXR file can trigger undefined behavior in OpenEXR

## Summary
Severity: Critical
Advisory: JLSEC-2026-811
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/JLSEC-2026-811
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=0 <3.4.12+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From versions 3.0.0 to before 3.2.9, 3.3.0 to before 3.3.11, and 3.4.0 to before 3.4.11, readVariableLengthInteger() decodes a variable-length integer from untrusted EXR input without bounding the shift count. After enough continuation bytes, the code executes a left shift by 70 on a 64-bit value, which is undefined behavior. This issue has been patched in versions 3.2.9, 3.3.11, and 3.4.11.

## References
- https://github.com/AcademySoftwareFoundation/openexr/commit/21eaa33bcbbb0c83a5fc42f6b6d65b70a996e63c
- https://github.com/AcademySoftwareFoundation/openexr/pull/2378
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-3c67-4wwp-w52m
