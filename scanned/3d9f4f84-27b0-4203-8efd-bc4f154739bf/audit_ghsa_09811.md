# [M] yard: Possible arbitrary path traversal and file access via yard server

## Summary
Severity: Medium
Advisory: GHSA-3jfp-46x4-xgfj
CVE: CVE-2026-41493
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-3jfp-46x4-xgfj
Type: github-advisory

## Affected
- RubyGems: `yard` — affected >=0 <0.9.42

## Details
### Impact

A path traversal vulnerability was discovered in YARD <= 0.9.41 when using yard server to serve documentation. This bug would allow unsanitized HTTP requests to access arbitrary files on the machine of a yard server host under certain conditions.

The original patch in [GHSA-xfhh-rx56-rxcr](https://github.com/lsegal/yard/security/advisories/GHSA-xfhh-rx56-rxcr) was incorrectly applied.

### Patches

Please upgrade to YARD v0.9.42 immediately if you are relying on yard server to host documentation in any untrusted environments without WEBrick and rely on `--docroot`.

### Workarounds

For users who cannot upgrade, it is possible to perform path sanitization of HTTP requests at your webserver level. WEBrick, for example, can perform such sanitization by default (which you can use via yard server -s webrick), as can certain rules in your webserver configuration.

## References
- https://github.com/lsegal/yard/security/advisories/GHSA-3jfp-46x4-xgfj
- https://nvd.nist.gov/vuln/detail/CVE-2026-41493
- https://github.com/lsegal/yard
- https://github.com/lsegal/yard/releases/tag/v0.9.42
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/yard/CVE-2026-41493.yml
