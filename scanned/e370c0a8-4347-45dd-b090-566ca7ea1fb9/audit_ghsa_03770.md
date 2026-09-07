# [H] Unintended Require in larvitbase-api

## Summary
Severity: High
Advisory: GHSA-xf27-jqwv-gf3r
CVE: CVE-2019-5479
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-09-11
Source: https://github.com/advisories/GHSA-xf27-jqwv-gf3r
Type: github-advisory

## Affected
- npm: `larvitbase-api` — affected >=0 <0.5.5

## Details
Versions of `larvitbase-api` prior to 0.5.4 are vulnerable to an Unintended Require. The package exposes an API endpoint and passes a GET parameter unsanitized to an `require()` call. This allows attackers to execute any `.js` file in the same folder as the server is running.


## Recommendation

Upgrade to version 0.5.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5479
- https://hackerone.com/reports/566056
- https://www.npmjs.com/advisories/1120
