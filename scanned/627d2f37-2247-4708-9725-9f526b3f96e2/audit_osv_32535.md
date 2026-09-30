# [M] Libsoup: segmentation fault when parsing malformed data uri

## Summary
Severity: Medium
Advisory: CVE-2025-32051
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-32051
Type: osv

## Details
A flaw was found in libsoup. The libsoup soup_uri_decode_data_uri() function may crash when processing malformed data URI. This flaw allows an attacker to cause a denial of service (DoS).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2025-32051
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32051.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32051
- https://bugzilla.redhat.com/show_bug.cgi?id=2357068
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/401
- https://gitlab.gnome.org/GNOME/libsoup/
