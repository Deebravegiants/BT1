# [H] CVE-2025-14576

## Summary
Severity: High
Advisory: CVE-2025-14576
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2025-14576
Type: osv

## Details
Insufficient validation of node IDs in Qt SVG module allows arbitrary QML/JavaScript code injection when loading malicious SVG files through the VectorImage component in Qt Quick. While QML execution is typically more restricted than native code execution, this could still lead to denial of service, information disclosure, or other impacts depending on the application's privilege level and data access.

## References
- https://access.redhat.com/security/cve/CVE-2025-14576
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-14576.json
- https://access.redhat.com/errata/RHSA-2026:20567
- https://access.redhat.com/errata/RHSA-2026:24987
- https://access.redhat.com/errata/RHSA-2026:7620
- https://access.redhat.com/errata/RHSA-2026:7846
- https://bugzilla.redhat.com/show_bug.cgi?id=2464114
- https://codereview.qt-project.org/c/qt/qtdeclarative/+/697273
