# [H] dustjs-linkedin vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-c6rp-wrp9-qr4q
CVE: CVE-2021-4264
CWE: CWE-1321, CWE-74, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-21
Source: https://github.com/advisories/GHSA-c6rp-wrp9-qr4q
Type: github-advisory

## Affected
- npm: `dustjs-linkedin` — affected >=0 <3.0.0

## Details
A vulnerability was found in LinkedIn dustjs prior to version 3.0.0 and classified as problematic. Affected by this issue is some unknown functionality. The manipulation leads to improperly controlled modification of object prototype attributes ('prototype pollution'). The attack may be launched remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 3.0.0 can address this issue. The name of the patch is ddb6523832465d38c9d80189e9de60519ac307c3. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-216464.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4264
- https://github.com/linkedin/dustjs/issues/804
- https://github.com/linkedin/dustjs/pull/805
- https://github.com/linkedin/dustjs/commit/ddb6523832465d38c9d80189e9de60519ac307c3
- https://github.com/linkedin/dustjs
- https://github.com/linkedin/dustjs/releases/tag/v3.0.0
- https://vuldb.com/?ctiid.216464
- https://vuldb.com/?id.216464
