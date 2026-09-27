# [M] GHSL-2024-228: GStreamer has an out-of-bounds write in SSA subtitle parser

## Summary
Severity: Medium
Advisory: CVE-2024-47541
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47541
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components. An OOB-write vulnerability has been identified in the gst_ssa_parse_remove_override_codes function of the gstssaparse.c file. This function is responsible for parsing and removing SSA (SubStation Alpha) style override codes, which are enclosed in curly brackets ({}). The issue arises when a closing curly bracket "}" appears before an opening curly bracket "{" in the input string. In this case, memmove() incorrectly duplicates a substring. With each successive loop iteration, the size passed to memmove() becomes progressively larger (strlen(end+1)), leading to a write beyond the allocated memory bounds. This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0023.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00021.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47541.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47541
- https://securitylab.github.com/advisories/GHSL-2024-228_GStreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8036.patch
