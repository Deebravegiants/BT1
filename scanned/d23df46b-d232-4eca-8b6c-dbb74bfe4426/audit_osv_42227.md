# [C] FFmpeg 3.4 - 8.1.2 vf_floodfill Out-of-Bounds Write via filter_frame()

## Summary
Severity: Critical
Advisory: CVE-2026-65705
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65705
Type: osv

## Details
FFmpeg versions 3.4 through 8.1.2 contain an out-of-bounds write vulnerability in the vf_floodfill video filter that allows attackers to corrupt heap memory by supplying a dynamically sized video stream with filtergraph reinitialization disabled via -reinit_filter 0. When config_input() allocates the points traversal stack based on initial frame dimensions and a subsequent larger frame is processed, filter_frame() performs flood-fill neighbor pushes beyond the original allocation boundary, resulting in heap corruption and process crash with potential for code execution depending on heap layout and process hardening.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65705.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65705
- https://www.vulncheck.com/advisories/ffmpeg-vf-floodfill-out-of-bounds-write-via-filter-frame
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23780
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/f186c50cf53aec20e9a29059cb22ca3f2d59201c
