# [M] JLSEC-2026-1280

## Summary
Severity: Medium
Advisory: JLSEC-2026-1280
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1280
Type: osv

## Affected
- Julia: `Soup3_jll` — affected unspecified

## Details
A flaw was found in libsoup. The package is vulnerable to a heap buffer over-read when sniffing content via the `skip_insight_whitespace()` function. Libsoup clients may read one byte out-of-bounds in response to a crafted HTTP response by an HTTP server.

## References
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
- https://bugzilla.redhat.com/show_bug.cgi?id=2354669
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/422
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/422
- https://lists.debian.org/debian-lts-announce/2025/04/msg00036.html
