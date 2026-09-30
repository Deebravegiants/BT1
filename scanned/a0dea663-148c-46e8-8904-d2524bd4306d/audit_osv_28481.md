# [H] CVE-2024-33531

## Summary
Severity: High
Advisory: CVE-2024-33531
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-04-24
Source: https://osv.dev/vulnerability/CVE-2024-33531
Type: osv

## Details
cdbattags lua-resty-jwt 0.2.3 allows attackers to bypass all JWT-parsing signature checks by crafting a JWT with an enc header with the value A256GCM.

## References
- https://insinuator.net/2023/10/lua-resty-jwt-authentication-bypass/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33531.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33531
- https://github.com/cdbattags/lua-resty-jwt/issues/61
- https://github.com/cdbattags/lua-resty-jwt/commit/d1558e2afefe868fea1e7e9a4b04ea94ab678a85
