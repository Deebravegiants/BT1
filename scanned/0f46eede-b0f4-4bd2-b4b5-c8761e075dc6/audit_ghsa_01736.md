# [H] Machine-In-The-Middle in lix

## Summary
Severity: High
Advisory: GHSA-q8xg-8xwf-m598
CVE: CVE-2020-10800
CWE: CWE-544, CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-04-16
Source: https://github.com/advisories/GHSA-q8xg-8xwf-m598
Type: github-advisory

## Affected
- npm: `lix` — affected >=0

## Details
All versions of `lix` are vulnerable to Machine-In-The-Middle. The package accepts downloads with `http` and follows `location` header redirects for package downloads. This allows for an attacker in a privileged network position to intercept a lix package installation and redirect the download to a malicious source.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10800
- https://github.com/lix-pm/lix.client
- https://www.npmjs.com/advisories/1306
