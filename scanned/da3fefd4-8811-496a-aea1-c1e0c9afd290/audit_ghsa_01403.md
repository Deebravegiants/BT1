# [H] Denial of Service in subtext

## Summary
Severity: High
Advisory: GHSA-2mvq-xp48-4c77
CWE: CWE-400
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-2mvq-xp48-4c77
Type: github-advisory

## Affected
- npm: `subtext` — affected >=0.0.0

## Details
All versions of `subtext` are vulnerable to Denial of Service (DoS). The package fails to enforce the `maxBytes` configuration for payloads with chunked encoding that are written to the file system. This allows attackers to send requests with arbitrary payload sizes, which may exhaust system resources leading to Denial of Service.


## Recommendation

This package is not actively maintained and has been moved to `@hapi/subtext` where version 6.1.2.

## References
- https://github.com/hapijs/subtext/issues/72
- https://github.com/hapijs/subtext
- https://www.npmjs.com/advisories/1168
