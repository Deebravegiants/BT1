# [H] Denial of Service in @hapi/subtext

## Summary
Severity: High
Advisory: GHSA-4rgj-8mq3-hggj
CWE: CWE-400
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-4rgj-8mq3-hggj
Type: github-advisory

## Affected
- npm: `@hapi/subtext` — affected >=0 <6.1.2

## Details
Versions of `@hapi/subtext` prior to 6.1.2 are vulnerable to Denial of Service (DoS). The package fails to enforce the `maxBytes` configuration for payloads with chunked encoding that are written to the file system. This allows attackers to send requests with arbitrary payload sizes, which may exhaust system resources leading to Denial of Service.


## Recommendation

Upgrade to version 6.1.2 or later.

## References
- https://github.com/hapijs/subtext/issues/72
- https://www.npmjs.com/advisories/1165
