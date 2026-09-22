# [C] Heap-memory write in FFMPEG

## Summary
Severity: Critical
Advisory: CVE-2022-2566
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-2566
Type: osv

## Details
A heap out-of-bounds memory write exists in FFMPEG since version 5.1. The size calculation in `build_open_gop_key_points()` goes through all entries in the loop and adds `sc->ctts_data[i].count` to `sc->sample_offsets_count`. This can lead to an integer overflow resulting in a small allocation with `av_calloc()`. An attacker can cause remote code execution via a malicious mp4 file. We recommend upgrading past commit c953baa084607dd1d84c3bfcce3cf6a87c3e6e05

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2566.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2566
- https://github.com/FFmpeg/FFmpeg/commit/c953baa084607dd1d84c3bfcce3cf6a87c3e6e05
