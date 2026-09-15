# [C] VLC media player 3.0.0 through 3.0.23 Heap Out-of-Bounds Write via Integer Overflow in Picture Allocation

## Summary
Severity: Critical
Advisory: CVE-2026-56711
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-56711
Type: osv

## Details
VLC media player computes the size of a picture buffer with 32-bit arithmetic and allocates from the wrapped result. In AllocatePicture in src/misc/picture.c the running total is accumulated as i_bytes += p->i_pitch * p->i_lines, and both plane_t fields are declared int in include/vlc_picture.h, so the multiplication is evaluated at 32 bits and wraps before it is widened to the size_t accumulator. The overflow check that precedes it divides in 64-bit arithmetic and therefore does not constrain the product, and the subsequent comparison against PICTURE_SW_SIZE_MAX examines the already wrapped value, so both guards pass. aligned_alloc then reserves the small wrapped size while the decoder writes scanlines sized from the original dimensions. A crafted PNG whose IHDR declares large width and height reaches this path through the image demuxer, whose only size guard is on the input file's byte count rather than the declared dimensions, and the decoder in modules/codec/png.c writes past the end of the allocation with attacker-influenced length and content. Opening the file directly or through a playlist entry is sufficient, with no non-default settings.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56711.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56711
- https://www.vulncheck.com/advisories/vlc-media-player-3.0.0-through-3.0.23-heap-out-of-bounds-write-via-integer-overflow-in-picture-allocation
- https://github.com/videolan/vlc
- https://github.com/videolan/vlc/blob/3.0.23/include/vlc_picture.h
- https://github.com/videolan/vlc/blob/3.0.23/modules/codec/png.c
- https://github.com/videolan/vlc/blob/3.0.23/modules/demux/image.c
- https://github.com/videolan/vlc/blob/3.0.23/src/misc/picture.c
