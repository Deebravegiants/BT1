# [M] Unauthorized File Access in harp

## Summary
Severity: Medium
Advisory: GHSA-46hv-7769-j7rx
CVE: CVE-2019-5437
CWE: CWE-548
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-06-13
Source: https://github.com/advisories/GHSA-46hv-7769-j7rx
Type: github-advisory

## Affected
- npm: `harp` — affected >=0 <0.40.2

## Details
Affected versions of `harp` are vulnerable to Unauthorized File Access. The package states that it ignores files and directories with names that start with an underscore, such as `_secret-folder`. If the underscore character is URL encoded the server delivers the file.

## Recommendation

Upgrade to version `0.40.2` or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5437
- https://github.com/sintaxi/harp/commit/1ec790baeeb2bfdb4584f1998af3d10a8fa31210
- https://hackerone.com/reports/453820
- https://www.npmjs.com/advisories/807
