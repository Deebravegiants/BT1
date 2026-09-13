# [H] Arbitrary File Write

## Summary
Severity: High
Advisory: CVE-2022-25297
Aliases: SNYK-UNMANAGED-DROGONFRAMEWORKDROGON-2407243
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-21
Source: https://osv.dev/vulnerability/CVE-2022-25297
Type: osv

## Details
This affects the package drogonframework/drogon before 1.7.5. The unsafe handling of file names during upload using HttpFile::save() method may enable attackers to write files to arbitrary locations outside the designated target folder.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/25xxx/CVE-2022-25297.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-25297
- https://snyk.io/vuln/SNYK-UNMANAGED-DROGONFRAMEWORKDROGON-2407243
- https://github.com/drogonframework/drogon/commit/3c785326c63a34aa1799a639ae185bc9453cb447
- https://github.com/drogonframework/drogon/pull/1174
