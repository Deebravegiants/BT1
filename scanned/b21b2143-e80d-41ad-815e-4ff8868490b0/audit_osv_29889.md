# [C] GHSL-2024-195: GStreamer has an OOB-write in convert_to_s334_1a

## Summary
Severity: Critical
Advisory: CVE-2024-47539
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47539
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components. An out-of-bounds write vulnerability was identified in the convert_to_s334_1a function in isomp4/qtdemux.c. The vulnerability arises due to a discrepancy between the size of memory allocated to the storage array and the loop condition i * 2 < ccpair_size. Specifically, when ccpair_size is even, the allocated size in storage does not match the loop's expected bounds, resulting in an out-of-bounds write. This bug allows for the overwriting of up to 3 bytes beyond the allocated bounds of the storage array. This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0007.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47539.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47539
- https://securitylab.github.com/advisories/GHSL-2024-195_Gstreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8059.patch
