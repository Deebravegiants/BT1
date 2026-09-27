# [C] GHSL-2024-117: GStreamer has an out-of-bounds write in Ogg demuxer

## Summary
Severity: Critical
Advisory: CVE-2024-47615
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47615
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components. An OOB-Write has been detected in the function gst_parse_vorbis_setup_packet within vorbis_parse.c. The integer size is read from the input file without proper validation. As a result, size can exceed the fixed size of the pad->vorbis_mode_sizes array (which size is 256). When this happens, the for loop overwrites the entire pad structure with 0s and 1s, affecting adjacent memory as well. This OOB-write can overwrite up to 380 bytes of memory beyond the boundaries of the pad->vorbis_mode_sizes array. This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0026.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00021.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47615.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47615
- https://securitylab.github.com/advisories/GHSL-2024-115_GHSL-2024-118_Gstreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8038.patch
