# [H] Webkit: webkitgtk / wpe webkit: out-of-bounds read and integer underflow vulnerability leading to dos

## Summary
Severity: High
Advisory: CVE-2025-13502
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/CVE-2025-13502
Type: osv

## Details
A flaw was found in WebKitGTK and WPE WebKit. This vulnerability allows an out-of-bounds read and integer underflow, leading to a UIProcess crash (DoS) via a crafted payload to the GLib remote inspector server.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://bugs.webkit.org/show_bug.cgi?id=302218
- https://access.redhat.com/errata/RHSA-2025:22789
- https://access.redhat.com/errata/RHSA-2025:22790
- https://access.redhat.com/errata/RHSA-2025:23110
- https://access.redhat.com/errata/RHSA-2025:23433
- https://access.redhat.com/errata/RHSA-2025:23434
- https://access.redhat.com/errata/RHSA-2025:23451
- https://access.redhat.com/errata/RHSA-2025:23452
- https://access.redhat.com/errata/RHSA-2025:23583
- https://access.redhat.com/errata/RHSA-2025:23591
- https://access.redhat.com/errata/RHSA-2025:23742
- https://access.redhat.com/errata/RHSA-2025:23743
- https://access.redhat.com/security/cve/CVE-2025-13502
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13502.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-13502
- https://bugzilla.redhat.com/show_bug.cgi?id=2416300
- https://github.com/WebKit/WebKit
