# [H] Validation bypass in frourio-express

## Summary
Severity: High
Advisory: CVE-2022-23624
Aliases: GHSA-mmj4-777p-fpq9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-07
Source: https://osv.dev/vulnerability/CVE-2022-23624
Type: osv

## Details
Frourio-express is a minimal full stack framework, for TypeScript. Frourio-express users who uses frourio-express version prior to v0.26.0 and integration with class-validator through `validators/` folder are subject to a input validation vulnerability. Validators do not work properly for request bodies and queries in specific situations and some input is not validated at all. Users are advised to update frourio to v0.26.0 or later and to install `class-transformer` and `reflect-metadata`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23624.json
- https://github.com/frouriojs/frourio-express/security/advisories/GHSA-mmj4-777p-fpq9
- https://nvd.nist.gov/vuln/detail/CVE-2022-23624
- https://github.com/frouriojs/frourio-express/commit/73ded5c6f9f1c126c0cb2d05c0505e9e4db142d2
