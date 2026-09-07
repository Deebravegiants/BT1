# [C] json-schema is vulnerable to Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-896r-f27r-55mw
CVE: CVE-2021-3918
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-19
Source: https://github.com/advisories/GHSA-896r-f27r-55mw
Type: github-advisory

## Affected
- npm: `json-schema` — affected >=0 <0.4.0

## Details
json-schema before version 0.4.0 is vulnerable to Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution').

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3918
- https://github.com/kriszyp/json-schema/commit/22f146111f541d9737e832823699ad3528ca7741
- https://github.com/kriszyp/json-schema/commit/b62f1da1ff5442f23443d6be6a92d00e65cba93a
- https://github.com/kriszyp/json-schema/commit/f6f6a3b02d667aa4ba2d5d50cc19208c4462abfa
- https://github.com/kriszyp/json-schema
- https://huntr.dev/bounties/bb6ccd63-f505-4e3a-b55f-cd2662c261a9
- https://lists.debian.org/debian-lts-announce/2022/12/msg00013.html
- https://security.netapp.com/advisory/ntap-20250117-0004
