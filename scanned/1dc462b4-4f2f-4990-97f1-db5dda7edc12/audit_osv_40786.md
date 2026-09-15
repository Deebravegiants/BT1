# [M] OpenEXR: OpenEXRUtil SampleCountChannel endEdit() can loop forever on UINT_MAX sample counts

## Summary
Severity: Medium
Advisory: CVE-2026-55373
Aliases: GHSA-mff9-68x3-h8rh
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-55373
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. Versions prior to 3.2.10, 3.3.12, and 3.4.13 contain an infinite-loop vulnerability in SampleCountChannel. The helper roundListSizeUp() rounds a sample-list size up to the next power of two using repeated unsigned left shifts, which terminates for normal values but fails for UINT_MAX: the sequence reaches 0x80000000, and the next left shift wraps the 32-bit value to 0. Because 0 remains less than UINT_MAX, the loop never progresses and never exits. The bug is reachable through public OpenEXRUtil APIs, either by editing the sample-count buffer through SampleCountChannel::Edit (whose destructor calls endEdit()) or by calling SampleCountChannel::set(x, y, UINT_MAX) on a valid pixel. This issue has been fixed in versions 3.2.10, 3.3.12, and 3.4.13.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-mff9-68x3-h8rh
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55373.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55373
