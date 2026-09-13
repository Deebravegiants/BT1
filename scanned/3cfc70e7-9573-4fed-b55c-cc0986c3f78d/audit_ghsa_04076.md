# [H] Denial of Service in foreman

## Summary
Severity: High
Advisory: GHSA-xm28-fw2x-fqv2
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-05-31
Source: https://github.com/advisories/GHSA-xm28-fw2x-fqv2
Type: github-advisory

## Affected
- npm: `foreman` — affected >=0 <3.0.1

## Details
All versions of `foreman` are vulnerable to Regular Expression Denial of Service when requests to it are made with a specially crafted path.


## Recommendation

Upgrade to version 3.0.1.

## References
- https://hackerone.com/reports/320586
- https://github.com/strongloop/node-foreman/blob/v2.0.0/forward.js#L30
- https://snyk.io/vuln/npm:foreman:20180429
- https://www.npmjs.com/advisories/645
