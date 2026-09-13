# [H] JLSEC-2026-1223

## Summary
Severity: High
Advisory: JLSEC-2026-1223
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-09
Source: https://osv.dev/vulnerability/JLSEC-2026-1223
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.8.1+0

## Details
In libexpat before 2.8.1, the computational complexity of attribute name collision checks allows a denial of service via moderately sized crafted XML input.

## References
- http://www.openwall.com/lists/oss-security/2026/05/11/16
- https://access.redhat.com/errata/RHSA-2026:22715
- https://access.redhat.com/errata/RHSA-2026:22721
- https://access.redhat.com/errata/RHSA-2026:23230
- https://access.redhat.com/errata/RHSA-2026:26319
- https://access.redhat.com/errata/RHSA-2026:27201
- https://access.redhat.com/errata/RHSA-2026:29197
- https://access.redhat.com/security/cve/CVE-2026-45186
- https://bugzilla.redhat.com/show_bug.cgi?id=2468575
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://github.com/libexpat/libexpat/pull/1216
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-45186.json
