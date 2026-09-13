# [H] CVE-2020-35666

## Summary
Severity: High
Advisory: CVE-2020-35666
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-23
Source: https://osv.dev/vulnerability/CVE-2020-35666
Type: osv

## Details
Steedos Platform through 1.21.24 allows NoSQL injection because the /api/collection/findone implementation in server/packages/steedos_base.js mishandles req.body validation, as demonstrated by MongoDB operator attacks such as an X-User-Id[$ne]=1 value.

## References
- https://github.com/steedos/steedos-platform/issues/1245
