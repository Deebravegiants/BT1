# [M] OpenEXR: OpenEXRUtil SampleCountChannel row setter heap has an out-of-bounds write vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-55059
Aliases: GHSA-54cp-3rq6-7mq8
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-55059
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. Versions prior to 3.2.10, 3.3.12 and 3.4.13 contain a heap out-of-bounds write in Imf_4_0::SampleCountChannel::set(int r, unsigned int newNumSamples[]). The row-based sample-count setter computes the target Y coordinate with dataWindow.min.x instead of dataWindow.min.y. For a valid deep image data window where min.x != min.y, a valid row index can be translated into an invalid Y coordinate, causing writes before the allocated _numSamples buffer. The vulnerability is reachable through the public OpenEXRUtil DeepImage API and can lead to heap corruption and process crashes. This issue has been fixed in versions 3.2.10, 3.3.12 and 3.4.13.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-54cp-3rq6-7mq8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55059.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55059
