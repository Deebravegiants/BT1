# [H] Gvfs: sftp: heap-based buffer overflow in read_reply()

## Summary
Severity: High
Advisory: CVE-2026-84268
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84268
Type: osv

## Details
A flaw was found in the SFTP backend in gvfs. When mounting a share and reading a file, a malicious SFTP server can cause read_reply() to process a length that exceeds the size requested by the client. The function does not verify the server-provided length against the allocated buffer size, causing the operation to write past the intended boundaries. This issue allows a malicious server to corrupt adjacent heap memory in the gvfsd-sftp process, resulting in a denial of service as the process aborts upon detecting the heap corruption or potentially allowing arbitrary code execution.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-84268
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84268.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84268
- https://bugzilla.redhat.com/show_bug.cgi?id=2526485
- https://gitlab.gnome.org/GNOME/gvfs/-/issues/862
- https://gitlab.gnome.org/GNOME/gvfs
