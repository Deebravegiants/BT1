# [H] Malcolm Vulnerable to Authorization Bypass via URI Normalization Differential in Nginx Lua RBAC

## Summary
Severity: High
Advisory: CVE-2026-63177
Aliases: GHSA-m5fr-rv3h-xg2r
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-63177
Type: osv

## Details
Malcolm is a network traffic analysis tool suite. Prior to version 26.07.0, role-based access control enforced in the Nginx OpenResty Lua layer evaluates the raw, unnormalized `ngx.var.request_uri`, while Nginx itself routes requests using the normalized path. An authenticated low-privilege user can prepend a traversal segment (for example `/x/../upload/...`) so that Nginx routes the request to a restricted backend while the Lua role check fails to match any rule and falls open, granting access it should deny. Version 26.07.0 fixes the issue.

## References
- https://github.com/cisagov/Malcolm/releases/tag/v26.07.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63177.json
- https://github.com/cisagov/Malcolm/security/advisories/GHSA-m5fr-rv3h-xg2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-63177
