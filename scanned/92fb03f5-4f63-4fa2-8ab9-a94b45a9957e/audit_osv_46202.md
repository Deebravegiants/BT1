# [H] Integer overflow in OpenEXR's `ImageChannel:resize`

## Summary
Severity: High
Advisory: JLSEC-2026-809
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/JLSEC-2026-809
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=0 <3.4.12+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From versions 3.0.0 to before 3.2.9, 3.3.0 to before 3.3.11, and 3.4.0 to before 3.4.11, there is an integer overflow in ImageChannel::resize that leads to heap OOB write via OpenEXRUtil public API. This issue has been patched in versions 3.2.9, 3.3.11, and 3.4.11.

## References
- https://access.redhat.com/errata/RHSA-2026:38498
- https://access.redhat.com/errata/RHSA-2026:38499
- https://access.redhat.com/errata/RHSA-2026:39024
- https://access.redhat.com/errata/RHSA-2026:39025
- https://access.redhat.com/errata/RHSA-2026:39026
- https://access.redhat.com/errata/RHSA-2026:39027
- https://access.redhat.com/security/cve/CVE-2026-41142
- https://bugzilla.redhat.com/show_bug.cgi?id=2467623
- https://github.com/AcademySoftwareFoundation/openexr/commit/0592ee539f33c122c90f09238579b902d838afb4
- https://github.com/AcademySoftwareFoundation/openexr/pull/2367
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-m25w-72cj-q6mg
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-41142.json
