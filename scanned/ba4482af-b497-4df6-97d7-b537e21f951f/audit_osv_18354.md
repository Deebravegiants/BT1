# [H] CVE-2020-26289

## Summary
Severity: High
Advisory: CVE-2020-26289
Aliases: GHSA-r92x-f52r-x54g
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-28
Source: https://osv.dev/vulnerability/CVE-2020-26289
Type: osv

## Details
date-and-time is an npm package for manipulating date and time. In date-and-time before version 0.14.2, there a regular expression involved in parsing which can be exploited to to cause a denial of service. This is fixed in version 0.14.2.

## References
- https://github.com/knowledgecode/date-and-time/security/advisories/GHSA-r92x-f52r-x54g
- https://www.npmjs.com/package/date-and-time
- https://github.com/knowledgecode/date-and-time/commit/9e4b501eacddccc8b1f559fb414f48472ee17c2a
