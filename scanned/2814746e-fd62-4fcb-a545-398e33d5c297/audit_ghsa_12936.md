# [H] zola Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-xvv9-5j67-3rpq
CVE: CVE-2023-40274
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-14
Source: https://github.com/advisories/GHSA-xvv9-5j67-3rpq
Type: github-advisory

## Affected
- crates.io: `zola` — affected >=0.13.0

## Details
An issue was discovered in zola 0.13.0 through 0.17.2. The custom implementation of a web server, available via the "zola serve" command, allows directory traversal. The `handle_request` function, used by the server to process HTTP requests, does not account for sequences of special path control characters (`../`) in the URL when serving a file, which allows one to escape the webroot of the server and read arbitrary files from the filesystem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40274
- https://github.com/getzola/zola/issues/2257
- https://github.com/getzola/zola/pull/2258
- https://github.com/getzola/zola
