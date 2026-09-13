# [M] protobufjs: Denial of Service via unbounded recursive JSON descriptor expansion

## Summary
Severity: Medium
Advisory: GHSA-jggg-4jg4-v7c6
CVE: CVE-2026-45740
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-jggg-4jg4-v7c6
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=0 <7.5.8
- npm: `protobufjs` — affected >=8.0.0 <8.2.0

## Details
## Summary

protobufjs could recurse without a depth limit while expanding nested JSON descriptors through `Root.fromJSON()` and `Namespace.addJSON()`.

A crafted JSON descriptor with deeply nested namespace definitions could cause the JavaScript call stack to be exhausted during descriptor loading.

## Impact

An attacker who can provide JSON descriptors loaded by an application may be able to crash the process or otherwise cause schema loading to fail with a stack overflow.

This affects applications that load JSON descriptors from untrusted sources with affected versions.

## Preconditions

- The application must load JSON descriptor data influenced by an attacker.
- The crafted descriptor must contain deeply nested `nested` namespace objects.
- The affected `Root.fromJSON()` / `Namespace.addJSON()` descriptor expansion path must process the crafted input.

## Workarounds

Avoid loading untrusted protobuf JSON descriptors with affected versions. If immediate upgrade is not possible, reject excessively nested descriptor structures at an outer validation boundary where feasible, or isolate descriptor loading in a process that can be safely restarted.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-jggg-4jg4-v7c6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45740
- https://github.com/protobufjs/protobuf.js
