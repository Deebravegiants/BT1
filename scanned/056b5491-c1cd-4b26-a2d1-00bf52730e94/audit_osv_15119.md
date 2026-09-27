# [M] CVE-2019-13615

## Summary
Severity: Medium
Advisory: CVE-2019-13615
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-16
Source: https://osv.dev/vulnerability/CVE-2019-13615
Type: osv

## Details
libebml before 1.3.6, as used in the MKV module in VideoLAN VLC Media Player binaries before 3.0.3, has a heap-based buffer over-read in EbmlElement::FindNextElement.

## References
- https://github.com/Matroska-Org/libebml/compare/release-1.3.5...release-1.3.6
- https://usn.ubuntu.com/4073-1/
- http://www.securityfocus.com/bid/109304
- https://trac.videolan.org/vlc/ticket/22474
- https://github.com/Matroska-Org/libebml/commit/05beb69ba60acce09f73ed491bb76f332849c3a0
- https://github.com/Matroska-Org/libebml/commit/b66ca475be967547af9a3784e720fbbacd381be6
