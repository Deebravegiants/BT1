# [H] EspoCRM has Admin TemplateManager path traversal that allows arbitrary file read write and delete

## Summary
Severity: High
Advisory: CVE-2026-33733
Aliases: GHSA-44c3-xjfp-3jrh
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33733
Type: osv

## Details
EspoCRM is an open source customer relationship management application. Prior to version 9.3.4, the admin template management endpoints accept attacker-controlled `name` and `scope` values and pass them into template path construction without normalization or traversal filtering. As a result, an authenticated admin can use `../` sequences to escape the intended template directory and read, create, overwrite, or delete arbitrary files that resolve to `body.tpl` or `subject.tpl` under the web application user's filesystem permissions. Version 9.3.4 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33733.json
- https://github.com/espocrm/espocrm/security/advisories/GHSA-44c3-xjfp-3jrh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33733
