# [H] Libsoup: denial of service attack to websocket server

## Summary
Severity: High
Advisory: CVE-2025-32049
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-32049
Type: osv

## Details
A flaw was found in libsoup. The SoupWebsocketConnection may accept a large WebSocket message, which may cause libsoup to allocate memory and lead to a denial of service (DoS).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:21657
- https://access.redhat.com/errata/RHSA-2025:8126
- https://access.redhat.com/errata/RHSA-2025:8128
- https://access.redhat.com/errata/RHSA-2025:8132
- https://access.redhat.com/errata/RHSA-2025:8139
- https://access.redhat.com/errata/RHSA-2025:8140
- https://access.redhat.com/errata/RHSA-2025:8252
- https://access.redhat.com/errata/RHSA-2025:8480
- https://access.redhat.com/errata/RHSA-2025:8481
- https://access.redhat.com/errata/RHSA-2025:8482
- https://access.redhat.com/errata/RHSA-2025:8663
- https://access.redhat.com/errata/RHSA-2025:9179
- https://access.redhat.com/security/cve/CVE-2025-32049
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32049.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32049
- https://bugzilla.redhat.com/show_bug.cgi?id=2357066
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/390
- https://gitlab.gnome.org/GNOME/libsoup/-/merge_requests/408
- https://gitlab.gnome.org/GNOME/libsoup/
