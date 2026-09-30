# [M] Gstreamer: incomplete fix of cve-2026-1940

## Summary
Severity: Medium
Advisory: CVE-2026-1940
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/CVE-2026-1940
Type: osv

## Details
An incomplete fix for CVE-2024-47778 allows an out-of-bounds read in gst_wavparse_adtl_chunk() function. The patch added a size validation check lsize + 8 > size, but it does not account for the GST_ROUND_UP_2(lsize) used in the actual offset calculation. When lsize is an odd number, the parser advances more bytes than validated, causing OOB read.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gstreamer.freedesktop.org/security/sa-2026-0001.html
- https://security-tracker.debian.org/tracker/CVE-2026-1940
- https://access.redhat.com/security/cve/CVE-2026-1940
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1940.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-1940
- https://bugzilla.redhat.com/show_bug.cgi?id=2436932
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/issues/4854
