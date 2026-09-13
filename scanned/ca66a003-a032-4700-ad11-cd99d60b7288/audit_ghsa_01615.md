# [H] Secret disclosure when containing characters that become URI encoded

## Summary
Severity: High
Advisory: GHSA-r2j6-p67h-q639
CVE: CVE-2020-26226
CWE: CWE-116
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-11-18
Source: https://github.com/advisories/GHSA-r2j6-p67h-q639
Type: github-advisory

## Affected
- npm: `semantic-release` — affected >=0 <17.2.3

## Details
### Impact

Secrets that would normally be masked by `semantic-release` can be accidentally disclosed if they contain characters that become encoded when included in a URL.

### Patches

Fixed in v17.2.3

### Workarounds

Secrets that do not contain characters that become encoded when included in a URL are already masked properly.

## References
- https://github.com/semantic-release/semantic-release/security/advisories/GHSA-r2j6-p67h-q639
- https://nvd.nist.gov/vuln/detail/CVE-2020-26226
- https://github.com/semantic-release/semantic-release/commit/ca90b34c4a9333438cc4d69faeb43362bb991e5a
