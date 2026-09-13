# [H] Webkit: webkitgtk: remote user-assisted information disclosure via file drag-and-drop

## Summary
Severity: High
Advisory: CVE-2025-13947
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/CVE-2025-13947
Type: osv

## Details
A flaw was found in WebKitGTK. This vulnerability allows remote, user-assisted information disclosure that can reveal any file the user is permitted to read via abusing the file drag-and-drop mechanism where WebKitGTK does not verify that drag operations originate from outside the browser.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://bugs.webkit.org/show_bug.cgi?id=271957
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
- https://access.redhat.com/security/cve/CVE-2025-13947
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13947.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-13947
- https://bugzilla.redhat.com/show_bug.cgi?id=2418576
- https://github.com/WebKit/WebKit
