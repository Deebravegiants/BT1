# [H] Command injection in google-it

## Summary
Severity: High
Advisory: GHSA-7xhv-mpjw-422f
CVE: CVE-2021-34083
CWE: CWE-74, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-7xhv-mpjw-422f
Type: github-advisory

## Affected
- npm: `google-it` — affected >=0

## Details
Google-it is a Node.js package which allows its users to send search queries to Google and receive the results in a JSON format. When using the 'Open in browser' option in versions up to 1.6.2, google-it will unsafely concat the result's link retrieved from google to a shell command, potentially exposing the server to RCE.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34083
- https://advisory.checkmarx.net/advisory/CX-2021-4777
- https://github.com/PatNeedham/google-it
- https://github.com/PatNeedham/google-it/blob/v1.6.2/lib/googleIt.js#L59
- https://github.com/PatNeedham/google-it/blob/v1.6.2/src/googleIt.js#L34
