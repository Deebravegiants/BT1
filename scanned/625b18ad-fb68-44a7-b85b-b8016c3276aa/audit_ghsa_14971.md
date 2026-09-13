# [H] Path traversal in saltstack

## Summary
Severity: High
Advisory: GHSA-2qw3-2wv6-p64x
CVE: CVE-2024-22232
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-27
Source: https://github.com/advisories/GHSA-2qw3-2wv6-p64x
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3005.5
- PyPI: `salt` — affected >=3006.0 <3006.6

## Details
A specially crafted url can be created which leads to a directory traversal in the salt file server.
A malicious user can read an arbitrary file from a Salt master’s filesystem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22232
- https://github.com/saltstack/salt/commit/e0cdb80b55123f4a024759ffcf2b3f0e0788e7ab
- https://github.com/saltstack/salt
- https://saltproject.io/security-announcements/2024-01-31-advisory
