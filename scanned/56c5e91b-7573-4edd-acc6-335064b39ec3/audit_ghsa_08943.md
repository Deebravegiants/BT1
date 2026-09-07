# [M] protobuf.js: Denial of service from crafted field names in generated code

## Summary
Severity: Medium
Advisory: GHSA-2pr8-phx7-x9h3
CVE: CVE-2026-44294
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-2pr8-phx7-x9h3
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=0 <7.5.6
- npm: `protobufjs` — affected >=8.0.0 <8.0.2

## Details
## Summary

protobufjs generated JavaScript property accessors from schema-controlled field and oneof names. Certain control characters in field names were not escaped before being embedded into generated function bodies. A crafted schema or JSON descriptor could therefore cause generated encode, decode, verify, or conversion functions to fail during compilation.

## Impact

An attacker who can provide or influence a protobuf schema or JSON descriptor may be able to make affected message types unusable by causing protobufjs runtime code generation to throw a syntax error.

This is a denial of service issue for applications that load untrusted schemas or descriptors. Applications that only use trusted, application-defined schemas are not directly affected by this issue.

The issue is not known to allow code execution by itself.

## Preconditions

- The application must allow an attacker to control or influence a protobuf schema or JSON descriptor.
- The crafted input must define a field name containing control characters that reach generated JavaScript property access.
- The application must perform an operation that triggers protobufjs code generation for the affected type, such as encode, decode, verify, `fromObject`, or `toObject`.

## Workarounds

Do not load protobuf schemas or JSON descriptors from untrusted sources with affected versions. If untrusted schemas must be accepted, validate field names before loading them and reject names containing control characters.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-2pr8-phx7-x9h3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44294
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v7.5.6
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v8.0.2
