# [M] PEAR HTTP_Request2 vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-w7gh-f2fm-9q8r
CVE: CVE-2025-43717
CWE: CWE-531, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-17
Source: https://github.com/advisories/GHSA-w7gh-f2fm-9q8r
Type: github-advisory

## Affected
- Packagist: `pear/http_request2` — affected >=0 <2.7.0

## Details
In PEAR HTTP_Request2 before 2.7.0, multiple files in the tests directory, notably tests/_network/getparameters.php and tests/_network/postparameters.php, reflect any GET or POST parameters, leading to XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43717
- https://github.com/pear/HTTP_Request2/commit/07925aa77e441dba0ff0fa973a09802729cb838f
- https://github.com/pear/HTTP_Request2/commit/265e05f9e08a28a38a57219516a8e4e2dfdbb147
- https://github.com/pear/HTTP_Request2
- https://github.com/pear/HTTP_Request2/blob/b1c61b71128045734d757c4d3d436457ace80ea7/package.xml#L24
- https://github.com/pear/HTTP_Request2/compare/v2.6.0...v2.7.0
