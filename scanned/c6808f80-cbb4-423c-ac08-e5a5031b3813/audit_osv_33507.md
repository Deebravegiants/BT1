# [M] Libsoup: null pointer dereference in libsoup may lead to denial of service

## Summary
Severity: Medium
Advisory: CVE-2025-4476
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-4476
Type: osv

## Details
A denial-of-service vulnerability has been identified in the libsoup HTTP client library. This flaw can be triggered when a libsoup client receives a 401 (Unauthorized) HTTP response containing a specifically crafted domain parameter within the WWW-Authenticate header. Processing this malformed header can lead to a crash of the client application using libsoup. An attacker could exploit this by setting up a malicious HTTP server. If a user's application using the vulnerable libsoup library connects to this malicious server, it could result in a denial-of-service. Successful exploitation requires tricking a user's client application into connecting to the attacker's malicious server.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2025-4476
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4476.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4476
- https://bugzilla.redhat.com/show_bug.cgi?id=2366513
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/440
- https://gitlab.gnome.org/GNOME/libsoup
- https://gitlab.gnome.org/GNOME/libsoup/-/work_items/440
