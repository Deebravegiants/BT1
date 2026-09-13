# [M] CVE-2021-39234

## Summary
Severity: Medium
Advisory: CVE-2021-39234
Aliases: GHSA-c8cw-2c5j-xff3
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-11-19
Source: https://osv.dev/vulnerability/CVE-2021-39234
Type: osv

## Details
In Apache Ozone versions prior to 1.2.0, Authenticated users knowing the ID of an existing block can craft specific request allowing access those blocks, bypassing other security checks like ACL.

## References
- http://www.openwall.com/lists/oss-security/2021/11/19/5
- https://mail-archives.apache.org/mod_mbox/ozone-dev/202111.mbox/%3C97d65498-7f8c-366f-1bea-5a74b6378f0d%40apache.org%3E
