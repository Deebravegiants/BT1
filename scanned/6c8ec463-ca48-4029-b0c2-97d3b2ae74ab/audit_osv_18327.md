# [H] CVE-2020-26207

## Summary
Severity: High
Advisory: CVE-2020-26207
Aliases: GHSA-rfjh-m356-mpqf
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-11-04
Source: https://osv.dev/vulnerability/CVE-2020-26207
Type: osv

## Details
DatabaseSchemaViewer before version 2.7.4.3 is vulnerable to arbitrary code execution if a user is tricked into opening a specially crafted `.dbschema` file. The patch was released in v2.7.4.3. As a workaround, ensure `.dbschema` files from untrusted sources are not opened.

## References
- https://github.com/martinjw/dbschemareader/releases/tag/2.7.4.3
- https://github.com/martinjw/dbschemareader/security/advisories/GHSA-rfjh-m356-mpqf
- https://github.com/martinjw/dbschemareader/commit/4c0ab7b1fd8c4e3140f9fd54d303f107a9c8d994
