# [H] CVE-2020-27848

## Summary
Severity: High
Advisory: CVE-2020-27848
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-30
Source: https://osv.dev/vulnerability/CVE-2020-27848
Type: osv

## Details
dotCMS before 20.10.1 allows SQL injection, as demonstrated by the /api/v1/containers orderby parameter. The PaginatorOrdered classes that are used to paginate results of a REST endpoints do not sanitize the orderBy parameter and in some cases it is vulnerable to SQL injection attacks. A user must be an authenticated manager in the dotCMS system to exploit this vulnerability.

## References
- https://github.com/dotCMS/core/compare/v5.3.8.1...v20.10.1
- https://github.com/dotCMS/core/issues/19500
