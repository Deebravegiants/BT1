# [M] Libsoup: null pointer dereference on libsoup through  function "sniff_mp4" in soup-content-sniffer.c

## Summary
Severity: Medium
Advisory: CVE-2025-32909
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-04-14
Source: https://osv.dev/vulnerability/CVE-2025-32909
Type: osv

## Details
A flaw was found in libsoup. SoupContentSniffer may be vulnerable to a NULL pointer dereference in the sniff_mp4 function. The HTTP server may cause the libsoup client to crash.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/04/msg00036.html
- https://access.redhat.com/errata/RHSA-2025:8292
- https://access.redhat.com/security/cve/CVE-2025-32909
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32909.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32909
- https://bugzilla.redhat.com/show_bug.cgi?id=2359353
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/431
- https://gitlab.gnome.org/GNOME/libsoup/
