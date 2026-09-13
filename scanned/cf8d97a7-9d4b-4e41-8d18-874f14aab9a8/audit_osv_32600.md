# [M] Libsoup: null pointer dereference in client when server  omits the "nonce" parameter in an unauthorized response with digest  authentication

## Summary
Severity: Medium
Advisory: CVE-2025-32912
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-04-14
Source: https://osv.dev/vulnerability/CVE-2025-32912
Type: osv

## Details
A flaw was found in libsoup, where SoupAuthDigest is vulnerable to a NULL pointer dereference. The HTTP server may cause the libsoup client to crash.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/04/msg00036.html
- https://access.redhat.com/errata/RHSA-2025:7505
- https://access.redhat.com/security/cve/CVE-2025-32912
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32912.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32912
- https://bugzilla.redhat.com/show_bug.cgi?id=2359356
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/434
- https://gitlab.gnome.org/GNOME/libsoup/
