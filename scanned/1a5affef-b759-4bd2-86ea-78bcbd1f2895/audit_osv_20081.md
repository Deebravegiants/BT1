# [C] CVE-2021-30108

## Summary
Severity: Critical
Advisory: CVE-2021-30108
Aliases: GHSA-gc45-j3m5-8qfq
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-05-24
Source: https://osv.dev/vulnerability/CVE-2021-30108
Type: osv

## Details
Feehi CMS 2.1.1 is affected by a Server-side request forgery (SSRF) vulnerability. When the user modifies the HTTP Referer header to any url, the server can make a request to it.

## References
- https://github.com/liufee/cms/issues/57
