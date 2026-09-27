# [C] GHSL-2024-197: GStreamer uses uninitialized stack memory in Matroska/WebM demuxer

## Summary
Severity: Critical
Advisory: CVE-2024-47540
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47540
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components. An uninitialized stack variable vulnerability has been identified in the gst_matroska_demux_add_wvpk_header function within matroska-demux.c. When size < 4, the program calls gst_buffer_unmap with an uninitialized map variable. Then, in the gst_memory_unmap function, the program will attempt to unmap the buffer using the uninitialized map variable, causing a function pointer hijack, as it will jump to mem->allocator->mem_unmap_full or mem->allocator->mem_unmap. This vulnerability could allow an attacker to hijack the execution flow, potentially leading to code execution. This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0017.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47540.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47540
- https://securitylab.github.com/advisories/GHSL-2024-197_GStreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8057.patch
