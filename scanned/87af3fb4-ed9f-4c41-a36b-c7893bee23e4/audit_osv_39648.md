# [C] OpenProject: Pre-authentication RCE in openproject/openproject Docker image via default `SECRET_KEY_BASE=OVERWRITE_ME` and `cookies_serializer = :marshal`

## Summary
Severity: Critical
Advisory: CVE-2026-46386
Aliases: GHSA-r85r-gjq2-f83r
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-46386
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to , the official openproject/openproject Docker image ships ENV SECRET_KEY_BASE=OVERWRITE_ME as the default Rails master key. Combined with cookies_serializer = :marshal, this gives any logged-in user a deterministic Marshal-deserialization path reachable via the /my/two_factor_devices cookie reader This vulnerability is fixed in .

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46386.json
- https://github.com/opf/openproject/security/advisories/GHSA-r85r-gjq2-f83r
- https://nvd.nist.gov/vuln/detail/CVE-2026-46386
