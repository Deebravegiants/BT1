# [H] CVE-2021-41243

## Summary
Severity: High
Advisory: CVE-2021-41243
Aliases: GHSA-7rpc-9m88-cf9w
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-26
Source: https://osv.dev/vulnerability/CVE-2021-41243
Type: osv

## Details
There is a Potential Zip Slip Vulnerability and OS Command Injection Vulnerability on the management system of baserCMS. Users with permissions to upload files may upload crafted zip files which may execute arbitrary commands on the host operating system. This is a vulnerability that needs to be addressed when the management system is used by an unspecified number of users. If you are eligible, please update to the new version as soon as possible.

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-7rpc-9m88-cf9w
- https://github.com/baserproject/basercms/commit/9088b99c329d1faff3a2f1269f37b9a9d8d5f6ff
