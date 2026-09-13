# [M] Gdk-pixbuf: gdk-pixbuf: invalid write in jpeg icc profile parser on error recovery

## Summary
Severity: Medium
Advisory: CVE-2026-81893
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81893
Type: osv

## Details
A flaw was found in gdk-pixbuf. When loading a specially crafted JPEG image containing chunked ICC profile markers, an error during ICC profile parsing can leave stale size metadata after the profile buffer is freed. A subsequent allocation in the same decode can cause an out-of-bounds write, potentially crashing the application. To exploit this flaw, an application using gdk-pixbuf must process the malicious JPEG image.

Affected version >= 2.26.4

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-81893
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81893.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81893
- https://bugzilla.redhat.com/show_bug.cgi?id=2524834
- https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/commit/efe658674bd103d1c9bf50809d5767a3f6dd5a01
- https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/merge_requests/278
