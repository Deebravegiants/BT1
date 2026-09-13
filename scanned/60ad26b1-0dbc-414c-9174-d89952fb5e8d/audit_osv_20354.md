# [H] CVE-2021-3309

## Summary
Severity: High
Advisory: CVE-2021-3309
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/CVE-2021-3309
Type: osv

## Details
packages/wekan-ldap/server/ldap.js in Wekan before 4.87 can process connections even though they are not authorized by the Certification Authority trust store,

## References
- https://github.com/wekan/wekan/releases/tag/v4.87
- https://github.com/wekan/wekan/issues/3482
- https://github.com/wekan/wekan/pull/3483/commits/31f89121fecca5a761b05cc3a26d4f237e90b484
