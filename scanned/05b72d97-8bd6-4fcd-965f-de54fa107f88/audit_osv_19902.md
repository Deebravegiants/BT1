# [H] CVE-2021-27516

## Summary
Severity: High
Advisory: CVE-2021-27516
Aliases: GHSA-p6j9-7xhc-rhwp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-22
Source: https://osv.dev/vulnerability/CVE-2021-27516
Type: osv

## Details
URI.js (aka urijs) before 1.19.6 mishandles certain uses of backslash such as http:\/ and interprets the URI as a relative path.

## References
- https://github.com/medialize/URI.js/releases/tag/v1.19.6
- https://github.com/medialize/URI.js/commit/a1ad8bcbc39a4d136d7e252e76e957f3ece70839
- https://advisory.checkmarx.net/advisory/CX-2021-4305
