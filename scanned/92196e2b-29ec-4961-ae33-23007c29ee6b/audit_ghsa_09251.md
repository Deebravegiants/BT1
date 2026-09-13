# [H] protobuf.js: Denial of service through unbounded protobuf recursion

## Summary
Severity: High
Advisory: GHSA-685m-2w69-288q
CVE: CVE-2026-44289
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-685m-2w69-288q
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=0 <7.5.6
- npm: `protobufjs` — affected >=8.0.0 <8.0.2

## Details
## Summary

protobufjs could recurse without a depth limit while decoding nested protobuf data. This affected both skipping unknown group fields and generated decoding of nested message fields.

A crafted protobuf binary payload could cause the JavaScript call stack to be exhausted during decoding.

## Impact

An attacker who can provide protobuf binary data decoded by an application may be able to crash the process or otherwise cause decoding to fail with a stack overflow.

This affects applications that decode untrusted protobuf binary input with affected versions.

## Preconditions

- The application must decode protobuf binary data influenced by an attacker.
- The crafted input must contain deeply nested protobuf structures, such as nested group tags or nested message fields.
- The affected decoder path must process the crafted input.

## Workarounds

Avoid decoding untrusted protobuf binary data with affected versions. If immediate upgrade is not possible, reject excessively nested messages at an outer protocol boundary where feasible, or isolate protobuf decoding in a process that can be safely restarted.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-685m-2w69-288q
- https://nvd.nist.gov/vuln/detail/CVE-2026-44289
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v7.5.6
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v8.0.2
