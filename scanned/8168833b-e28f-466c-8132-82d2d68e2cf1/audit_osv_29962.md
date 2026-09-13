# [M] GHSL-2024-263: Gstreamer NULL-pointer dereference in LRC subtitle parser

## Summary
Severity: Medium
Advisory: CVE-2024-47835
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47835
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components. A null pointer dereference vulnerability has been detected in the parse_lrc function within gstsubparse.c. The parse_lrc function calls strchr() to find the character ']' in the string line. The pointer returned by this call is then passed to g_strdup(). However, if the string line does not contain the character ']', strchr() returns NULL, and a call to g_strdup(start + 1) leads to a null pointer dereference. This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0029.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00021.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47835.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47835
- https://securitylab.github.com/advisories/GHSL-2024-263_Gstreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8039.patch
