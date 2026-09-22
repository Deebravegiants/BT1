# [M] Denial of Service in http-live-simulator

## Summary
Severity: Medium
Advisory: GHSA-xgp2-cc4r-7vf6
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-xgp2-cc4r-7vf6
Type: github-advisory

## Affected
- npm: `http-live-simulator` — affected >=0 <1.0.8

## Details
Versions of `http-live-simulator` prior to 1.0.8 are vulnerable to Denial of Service. The package fails to catch an exception that causes the Node process to crash, effectively shutting down the server. This allows an attacker to send an HTTP request that crashes the server.


## Recommendation

Upgrade to version 1.0.8 or later.

## References
- https://hackerone.com/reports/627376
- https://www.npmjs.com/advisories/1189
