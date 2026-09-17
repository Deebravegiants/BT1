# [H] Denial of Service in http-proxy-agent

## Summary
Severity: High
Advisory: GHSA-8w57-jfpm-945m
CWE: CWE-400
Ecosystem: npm
Published: 2019-06-11
Source: https://github.com/advisories/GHSA-8w57-jfpm-945m
Type: github-advisory

## Affected
- npm: `http-proxy-agent` — affected >=0 <2.1.0

## Details
Versions of `http-proxy-agent` before 2.1.0 are vulnerable to denial of service and uninitialized memory leak when unsanitized options are passed to `Buffer`. An attacker may leverage these unsanitized options to consume system resources.


## Recommendation

Update to version 2.1.0 or later.

## References
- https://hackerone.com/reports/321631
- https://github.com/TooTallNate/node-http-proxy-agent/blob/2.0.0/index.js#L80
- https://www.npmjs.com/advisories/607
