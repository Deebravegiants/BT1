# [H] Libsoup: heap buffer over-read in `skip_insignificant_space` when sniffing content

## Summary
Severity: High
Advisory: CVE-2025-2784
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-2784
Type: osv

## Details
A flaw was found in libsoup. The package is vulnerable to a heap buffer over-read when sniffing content via the skip_insight_whitespace() function. Libsoup clients may read one byte out-of-bounds in response to a crafted HTTP response by an HTTP server.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/04/msg00036.html
- https://access.redhat.com/errata/RHSA-2025:21657
- https://access.redhat.com/errata/RHSA-2025:7505
- https://access.redhat.com/errata/RHSA-2025:8126
- https://access.redhat.com/errata/RHSA-2025:8132
- https://access.redhat.com/errata/RHSA-2025:8139
- https://access.redhat.com/errata/RHSA-2025:8140
- https://access.redhat.com/errata/RHSA-2025:8252
- https://access.redhat.com/errata/RHSA-2025:8480
- https://access.redhat.com/errata/RHSA-2025:8481
- https://access.redhat.com/errata/RHSA-2025:8482
- https://access.redhat.com/errata/RHSA-2025:8663
- https://access.redhat.com/errata/RHSA-2025:9179
- https://access.redhat.com/security/cve/CVE-2025-2784
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2784.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2784
- https://bugzilla.redhat.com/show_bug.cgi?id=2354669
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/422
- https://gitlab.gnome.org/GNOME/libsoup/
