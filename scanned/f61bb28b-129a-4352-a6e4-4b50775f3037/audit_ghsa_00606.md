# [C] Critical severity vulnerability that affects event-stream and flatmap-stream

## Summary
Severity: Critical
Advisory: GHSA-mh6f-8j2x-4483
CWE: CWE-506
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-11-26
Source: https://github.com/advisories/GHSA-mh6f-8j2x-4483
Type: github-advisory

## Affected
- npm: `event-stream` — affected >=3.3.6 <4.0.0
- npm: `flatmap-stream` — affected >=0

## Details
The NPM package `flatmap-stream` is considered malicious.  A malicious actor added this package as a dependency to the NPM `event-stream` package in version `3.3.6`.  Users of `event-stream` are encouraged to downgrade to the last non-malicious version, `3.3.4`, or upgrade to the latest  4.x version. 

Users of `flatmap-stream` are encouraged to remove the dependency entirely.

## References
- https://github.com/dominictarr/event-stream/issues/116
- https://github.com/advisories/GHSA-mh6f-8j2x-4483
- https://github.com/dominictarr/event-stream
