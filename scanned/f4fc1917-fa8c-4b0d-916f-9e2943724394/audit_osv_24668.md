# [H] SQL injection of notes/search-by-tag

## Summary
Severity: High
Advisory: CVE-2023-24812
Aliases: GHSA-cgwp-vmr4-wx4q
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-22
Source: https://osv.dev/vulnerability/CVE-2023-24812
Type: osv

## Details
Misskey is an open source, decentralized social media platform. In versions prior to 13.3.3 SQL injection is possible due to insufficient parameter validation in the note search API by tag (notes/search-by-tag). This has been fixed in version 13.3.3. Users are advised to upgrade. Users unable to upgrade should block access to the `api/notes/search-by-tag` endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24812.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-cgwp-vmr4-wx4q
- https://nvd.nist.gov/vuln/detail/CVE-2023-24812
- https://github.com/misskey-dev/misskey/commit/ee74df68233adcd5b167258c621565f97c3b2306
