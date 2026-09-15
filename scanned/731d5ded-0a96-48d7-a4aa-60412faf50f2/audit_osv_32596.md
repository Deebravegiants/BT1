# [H] Libsoup: denial of service on libsoup through http/2 server

## Summary
Severity: High
Advisory: CVE-2025-32908
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-14
Source: https://osv.dev/vulnerability/CVE-2025-32908
Type: osv

## Details
A flaw was found in libsoup. The HTTP/2 server in libsoup may not fully validate the values of pseudo-headers :scheme, :authority, and :path, which may allow a user to cause a denial of service (DoS).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:7505
- https://access.redhat.com/security/cve/CVE-2025-32908
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32908.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32908
- https://bugzilla.redhat.com/show_bug.cgi?id=2359343
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/429
- https://gitlab.gnome.org/GNOME/libsoup/-/merge_requests/451
- https://gitlab.gnome.org/GNOME/libsoup/
