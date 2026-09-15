# [C] password leak with netrc and user in URL

## Summary
Severity: Critical
Advisory: CVE-2026-8926
Aliases: CURL-CVE-2026-8926
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-8926
Type: osv

## Details
When asking curl to use a `.netrc` file to find credentials and at the same
time specifying a URL with a username(without a password), like
`https://user@example.com/`, curl could wrongly get and use the password for
*another* user set in the `.netrc` file for that host if such a one exists and
there is no match for the specified user.

## References
- https://curl.se/docs/CVE-2026-8926.html
- https://curl.se/docs/CVE-2026-8926.json
- https://hackerone.com/reports/3735184
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8926.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8926
