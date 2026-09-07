# [H] Path Traversal vulnerability that affects yard

## Summary
Severity: High
Advisory: GHSA-xfhh-rx56-rxcr
CVE: CVE-2019-1020001
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-07-02
Source: https://github.com/advisories/GHSA-xfhh-rx56-rxcr
Type: github-advisory

## Affected
- RubyGems: `yard` — affected >=0 <0.9.20

## Details
## Possible arbitrary path traversal and file access via `yard server`

### Impact

A path traversal vulnerability was discovered in YARD <= 0.9.19 when using `yard server` to serve documentation. This bug would allow unsanitized HTTP requests to access arbitrary files on the machine of a yard server host under certain conditions.

Thanks to CuongMX from Viettel Cyber Security for discovering this vulnerability.

### Patches

Please upgrade to YARD v0.9.20 immediately if you are relying on yard server to host documentation in any untrusted environments.

### Workarounds

For users who cannot upgrade, it is possible to perform path sanitization of HTTP requests at your webserver level. WEBrick, for example, can perform such sanitization by default (which you can use via `yard server -s webrick`), as can certain rules in your webserver configuration.

## References
- https://github.com/lsegal/yard/security/advisories/GHSA-xfhh-rx56-rxcr
- https://nvd.nist.gov/vuln/detail/CVE-2019-1020001
- https://github.com/advisories/GHSA-xfhh-rx56-rxcr
- https://lists.debian.org/debian-lts-announce/2024/03/msg00006.html
