# [M] CVE-2026-79513

## Summary
Severity: Medium
Advisory: CVE-2026-79513
CVSS: 6.5 (CVSS:3.1/AC:L/AV:N/A:H/C:N/I:N/PR:N/S:U/UI:R)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-79513
Type: osv

## Details
A divide-by-zero vulnerability in the gf_dash_get_timeline_duration function (src/media_tools/dash_client.c) of GPAC v26.07.0 allows attackers to cause a Denial of Service (DoS) via a crafted MPD SegmentTimeline. Fixed in 2fd5a06ab226767900fd86edb5a1e8bfc1010640.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79513.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-79513
- https://github.com/gpac/gpac/issues/3862
- https://github.com/gpac/gpac/commit/2fd5a06ab226767900fd86edb5a1e8bfc1010640
