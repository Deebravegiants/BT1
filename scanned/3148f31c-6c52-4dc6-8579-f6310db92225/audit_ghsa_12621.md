# [H] Vapor vulnerable to denial of service in HTTP Range Request of FileMiddleware

## Summary
Severity: High
Advisory: GHSA-vj2m-9f5j-mpr5
CVE: CVE-2022-31005
CWE: CWE-190
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-07
Source: https://github.com/advisories/GHSA-vj2m-9f5j-mpr5
Type: github-advisory

## Affected
- SwiftURL: `github.com/vapor/vapor` — affected >=0 <4.60.3

## Details
Vapor is an HTTP web framework for Swift and [middleware](https://docs.vapor.codes/advanced/middleware/) is a logic chain between the client and a Vapor route handler. [FileMiddleware](https://docs.vapor.codes/advanced/middleware/#file-middleware) enables the serving of assets from the Public folder of a project to the client. 

Vapor before 4.60.3 is vulnerable to denial of service due to an integer overflow when given invalid range headers while using FileMiddleware. This is patched in 4.60.3.

## References
- https://github.com/vapor/vapor/security/advisories/GHSA-vj2m-9f5j-mpr5
- https://nvd.nist.gov/vuln/detail/CVE-2022-31005
- https://github.com/vapor/vapor/commit/953a349b539b3e0d3653585c8ffb50c427986df1
- https://github.com/vapor/vapor
- https://github.com/vapor/vapor/releases/tag/4.60.3
