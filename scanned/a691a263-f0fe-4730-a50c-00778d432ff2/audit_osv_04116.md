# [C] Apache HTTP Server: buffer overflow in mod_proxy_ajp via  ajp_msg_check_header()

## Summary
Severity: Critical
Advisory: BIT-apache-2026-28780
Aliases: CVE-2026-28780
Ecosystem: Bitnami
Published: 2026-05-07
Source: https://osv.dev/vulnerability/BIT-apache-2026-28780
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.67

## Details
Heap-based Buffer Overflow vulnerability in mod_proxy_ajp of Apache HTTP Server.
If mod_proxy_ajp connects to a malicious AJP server this AJP server can send a malicious AJP message back to mod_proxy_ajp and cause it to write 4 attacker controlled bytes after the end of a heap based buffer.

This issue affects Apache HTTP Server: through 2.4.66.

Users are recommended to upgrade to version 2.4.67, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/05/9
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-28780
- https://access.redhat.com/errata/RHSA-2026:21391
- https://access.redhat.com/errata/RHSA-2026:21433
- https://access.redhat.com/errata/RHSA-2026:22140
- https://access.redhat.com/errata/RHSA-2026:27200
- https://access.redhat.com/errata/RHSA-2026:27201
- https://access.redhat.com/security/cve/CVE-2026-28780
- https://bugzilla.redhat.com/show_bug.cgi?id=2466913
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-28780.json
- https://access.redhat.com/errata/RHSA-2026:36373
- https://access.redhat.com/errata/RHSA-2026:36831
- https://access.redhat.com/errata/RHSA-2026:36846
- https://access.redhat.com/errata/RHSA-2026:47046
- https://access.redhat.com/errata/RHSA-2026:62165
- https://access.redhat.com/errata/RHSA-2026:66323
