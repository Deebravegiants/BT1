# [M]  blamer vulnerable to Arbitrary Argument Injection via the blameByFile() API

## Summary
Severity: Medium
Advisory: GHSA-6f9p-g466-f8v8
CVE: CVE-2023-26143
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2023-09-19
Source: https://github.com/advisories/GHSA-6f9p-g466-f8v8
Type: github-advisory

## Affected
- npm: `blamer` — affected >=0 <1.0.4

## Details
Versions of the blamer package before 1.0.4 are vulnerable to Arbitrary Argument Injection via the blameByFile() API. The library does not sanitize for user input or validate the given file path conforms to a specific schema, nor does it properly pass command-line flags to the git binary using the double-dash POSIX characters (--) to communicate the end of options.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26143
- https://github.com/kucherenko/blamer/commit/0965877f115753371a2570f10a63c455d2b2cde3
- https://gist.github.com/lirantal/14c3686370a86461f555d3f0703e02f9
- https://github.com/kucherenko/blamer
- https://security.snyk.io/vuln/SNYK-JS-BLAMER-5731318
