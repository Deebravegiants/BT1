# [H] Path Traversal in socket.io-file

## Summary
Severity: High
Advisory: GHSA-9h4g-27m8-qjrg
CVE: CVE-2020-15779
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-07-07
Source: https://github.com/advisories/GHSA-9h4g-27m8-qjrg
Type: github-advisory

## Affected
- npm: `socket.io-file` — affected >=0

## Details
All versions of `socket.io-file` are vulnerable to Path Traversal. The package fails to sanitize user input and uses it to generate the file upload paths. The `socket.io-file::createFile` message contains a `name` option that is passed directly to `path.join()`.   It is possible to upload files to arbitrary folders on the server by sending relative paths on the `name` value, such as `../../test.js`.  The `uploadDir` and `rename` options can be used to define the file upload path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15779
- https://github.com/advisories/GHSA-9h4g-27m8-qjrg
- https://github.com/rico345100/socket.io-file
- https://www.npmjs.com/advisories/1519
- https://www.npmjs.com/package/socket.io-file
