# [C] JLSEC-2026-141

## Summary
Severity: Critical
Advisory: JLSEC-2026-141
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-141
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=0 <3.4.8+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. In `CompositeDeepScanLine::readPixels`, per-pixel totals are accumulated in `vector<unsigned int> total_sizes` for attacker-controlled large counts across many parts, `total_sizes`[ptr] wraps modulo 2^32.  `overall_sample_count` is then derived from wrapped totals and used in `samples[channel].resize(overall_sample_count)`. Decode pointer setup/consumption proceeds with true sample counts, and write operations in core unpack (`generic_unpack_deep_pointers`) overrun the undersized composite sample buffer. This vulnerability is fixed in v3.2.6, v3.3.8, and v3.4.6.

## References
- https://access.redhat.com/errata/RHSA-2026:12338
- https://access.redhat.com/errata/RHSA-2026:12339
- https://access.redhat.com/errata/RHSA-2026:12340
- https://access.redhat.com/errata/RHSA-2026:12341
- https://access.redhat.com/errata/RHSA-2026:16008
- https://access.redhat.com/errata/RHSA-2026:16009
- https://access.redhat.com/errata/RHSA-2026:16030
- https://access.redhat.com/errata/RHSA-2026:16174
- https://access.redhat.com/errata/RHSA-2026:7678
- https://access.redhat.com/errata/RHSA-2026:7682
- https://access.redhat.com/errata/RHSA-2026:8863
- https://access.redhat.com/errata/RHSA-2026:8869
- https://access.redhat.com/errata/RHSA-2026:8870
- https://access.redhat.com/errata/RHSA-2026:8871
- https://access.redhat.com/errata/RHSA-2026:8872
- https://access.redhat.com/errata/RHSA-2026:8888
- https://access.redhat.com/security/cve/CVE-2026-27622
- https://bugzilla.redhat.com/show_bug.cgi?id=2444251
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-cr4v-6jm6-4963
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27622.json
