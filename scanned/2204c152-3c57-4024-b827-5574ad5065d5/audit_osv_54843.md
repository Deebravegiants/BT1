# [M] CVE-2024-4982

## Summary
Severity: Medium
Advisory: CVE-2024-4982
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-05-12
Source: https://osv.dev/vulnerability/CVE-2024-4982
Type: osv

## Details
A directory traversal vulnerability was discovered in Pagure server. If a malicious user submits a specially cratfted git repository they could discover secrets on the server.

## References
- https://access.redhat.com/security/cve/CVE-2024-4982
- https://bugzilla.redhat.com/show_bug.cgi?id=2279411
- https://bugzilla.redhat.com/show_bug.cgi?id=2280726
- https://pagure.io/pagure/c/c43844d23c919133fc983fe8c0f1dfb3b86e67d0
