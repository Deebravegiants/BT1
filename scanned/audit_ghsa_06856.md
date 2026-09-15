# [M] protobufjs: Denial of Service via infinite loop in .proto option parsing

## Summary
Severity: Medium
Advisory: GHSA-j3f2-48v5-ccww
CVE: CVE-2026-59877
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-j3f2-48v5-ccww
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=7.5.0 <7.6.5
- npm: `protobufjs` — affected >=8.0.0 <8.6.6

## Details
## Summary

protobufjs parsed option names by advancing through schema tokens until it reached an `=` token, without checking for end of input. A crafted `.proto` schema that opens an option declaration but ends prematurely could cause the option parser to loop without ever terminating.

This affects the reflection parsing path (`parse`, `Root.load`, `Root.loadSync`).

## Impact

An attacker who can provide or influence `.proto` schema text parsed by an application may be able to cause the parsing call to never return. Because Node.js is single-threaded, the blocked event loop prevents all other work in the process, resulting in a denial of service that persists until the process is externally terminated.

Applications that only encode or decode protobuf binary data with trusted schemas are not directly affected.

## Preconditions

- The application must parse `.proto` schema text influenced by an attacker.
- The schema must be parsed through APIs such as `parse`, `Root.load`, or `Root.loadSync`.
- The crafted input must begin an option declaration that ends before its `=` assignment.

## Workarounds

Do not parse `.proto` schemas from untrusted sources with affected versions. If untrusted schema text must be accepted, isolate parsing in a process or worker that can be safely terminated and bound it with a timeout, so a non-returning parse call cannot deny service to the rest of the application.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-j3f2-48v5-ccww
- https://nvd.nist.gov/vuln/detail/CVE-2026-59877
- https://github.com/protobufjs/protobuf.js/pull/2352
- https://github.com/protobufjs/protobuf.js/commit/10fba6d54815ceecca8a06b9a6db490c8f5d2217
- https://github.com/protobufjs/protobuf.js/commit/fa5c73add738ceb471e74da8cc2f3727c3d0a69f
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v7.6.5
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v8.6.6
