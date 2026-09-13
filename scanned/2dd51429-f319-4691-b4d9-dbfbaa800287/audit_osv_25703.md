# [H] CVE-2023-4236

## Summary
Severity: High
Advisory: CVE-2023-4236
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-20
Source: https://osv.dev/vulnerability/CVE-2023-4236
Type: osv

## Details
A flaw in the networking code handling DNS-over-TLS queries may cause `named` to terminate unexpectedly due to an assertion failure. This happens when internal data structures are incorrectly reused under significant DNS-over-TLS query load.
This issue affects BIND 9 versions 9.18.0 through 9.18.18 and 9.18.11-S1 through 9.18.18-S1.

## References
- http://www.openwall.com/lists/oss-security/2023/09/20/2
- https://kb.isc.org/docs/cve-2023-4236
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VSK5V4W4OHPM3JTJGWAQD6CZW7SFD75B/
- https://security.netapp.com/advisory/ntap-20231013-0004/
- https://www.debian.org/security/2023/dsa-5504
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IPJLLTJCSDJJII7IIZPLTBQNWP7MZH7F/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U35OARLQCPMVCBBPHWBXY5M6XJLD2TZ5/
