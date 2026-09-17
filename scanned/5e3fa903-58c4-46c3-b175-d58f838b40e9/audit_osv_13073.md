# [M] CVE-2018-17235

## Summary
Severity: Medium
Advisory: CVE-2018-17235
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-20
Source: https://osv.dev/vulnerability/CVE-2018-17235
Type: osv

## Details
The function mp4v2::impl::MP4Track::FinishSdtp() in mp4track.cpp in libmp4v2 2.1.0 mishandles compatibleBrand while processing a crafted mp4 file, which leads to a heap-based buffer over-read, causing denial of service.

## References
- https://github.com/enzo1982/mp4v2/releases/tag/v2.1.0
- https://bugzilla.redhat.com/show_bug.cgi?id=1629451
