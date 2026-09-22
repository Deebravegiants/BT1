# [M] MeterSphere denial of service vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-32699
Aliases: GHSA-qffq-8gf8-mhq7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-32699
Type: osv

## Details
MeterSphere is an open source continuous testing platform. Version 2.9.1 and prior are vulnerable to denial of service. ​The `checkUserPassword` method is used to check whether the password provided by the user matches the password saved in the database, and the `CodingUtil.md5` method is used to encrypt the original password with MD5 to ensure that the password will not be saved in plain text when it is stored. If a user submits a very long password when logging in, the system will be forced to execute the long password MD5 encryption process, causing the server CPU and memory to be exhausted, thereby causing a denial of service attack on the server. This issue is fixed in version 2.10.0-lts with a maximum password length.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32699.json
- https://github.com/metersphere/metersphere/security/advisories/GHSA-qffq-8gf8-mhq7
- https://nvd.nist.gov/vuln/detail/CVE-2023-32699
- https://github.com/metersphere/metersphere/commit/c59e381d368990214813085a1a4877c5ef865411
