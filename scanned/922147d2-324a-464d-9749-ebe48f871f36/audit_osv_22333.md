# [C] Arbitrary File Write

## Summary
Severity: Critical
Advisory: CVE-2022-25299
Aliases: SNYK-UNMANAGED-CESANTAMONGOOSE-2404180
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2022-25299
Type: osv

## Details
This affects the package cesanta/mongoose before 7.6. The unsafe handling of file names during upload using mg_http_upload() method may enable attackers to write files to arbitrary locations outside the designated target folder.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/25xxx/CVE-2022-25299.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-25299
- https://snyk.io/vuln/SNYK-UNMANAGED-CESANTAMONGOOSE-2404180
- https://github.com/cesanta/mongoose/commit/c65c8fdaaa257e0487ab0aaae9e8f6b439335945
