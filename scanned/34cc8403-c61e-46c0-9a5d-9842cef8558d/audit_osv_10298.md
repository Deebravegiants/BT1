# [H] CVE-2017-14849

## Summary
Severity: High
Advisory: CVE-2017-14849
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-28
Source: https://osv.dev/vulnerability/CVE-2017-14849
Type: osv

## Details
Node.js 8.5.0 before 8.6.0 allows remote attackers to access unintended files, because a change to ".." handling was incompatible with the pathname validation used by unspecified community modules.

## References
- http://www.securityfocus.com/bid/101056
- https://nodejs.org/en/blog/vulnerability/september-2017-path-validation/
- https://twitter.com/nodejs/status/913131152868876288
