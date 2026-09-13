# [H] JLSEC-2026-289

## Summary
Severity: High
Advisory: JLSEC-2026-289
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-289
Type: osv

## Affected
- Julia: `Singular_jll` — affected >=0 <403.201.0+0

## Details
In Singular before 4.3.1, a predictable `/tmp` pathname is used (e.g., by sdb.cc), which allows local users to gain the privileges of other users via a procedure in a file under `/tmp`. NOTE: this CVE Record is about sdb.cc and similar files in the Singular interface that have predictable `/tmp` pathnames; this CVE Record is not about the lack of a safe temporary-file creation capability in the Singular language.

## References
- http://michael.orlitzky.com/cves/cve-2022-40299.xhtml
- https://github.com/Singular/Singular/commit/5f28fbf066626fa9c4a8f0e6408c0bb362fb386c
- https://github.com/Singular/Singular/issues/1137
