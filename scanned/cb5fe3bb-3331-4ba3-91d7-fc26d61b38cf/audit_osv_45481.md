# [C] When asking curl to use a `.netrc` file to find credentials and at the same time specifying a URL...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1215
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1215
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.11.1+0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=8.11.1+0 <8.21.0+0

## Details
When asking curl to use a `.netrc` file to find credentials and at the same
time specifying a URL with a username(without a password), like
`https://user@example.com/`, curl could wrongly get and use the password for
*another* user set in the `.netrc` file for that host if such a one exists and
there is no match for the specified user.

## References
- https://curl.se/docs/CVE-2026-8926.html
- https://curl.se/docs/CVE-2026-8926.json
- https://github.com/advisories/GHSA-vw2x-3w8j-rq82
- https://hackerone.com/reports/3735184
- https://nvd.nist.gov/vuln/detail/CVE-2026-8926
