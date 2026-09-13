# [M] protobufjs : Schema-derived names can shadow runtime-significant properties

## Summary
Severity: Medium
Advisory: GHSA-f38q-mgvj-vph7
CVE: CVE-2026-54269
CWE: CWE-674, CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-f38q-mgvj-vph7
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=0 <7.6.3
- npm: `protobufjs-cli` — affected >=2.0.0 <2.5.1
- npm: `protobufjs-cli` — affected >=0 <1.3.3
- npm: `protobufjs` — affected >=8.0.0 <8.6.0

## Details
## Summary

protobufjs accepted certain schema-derived names that could collide with properties used by protobufjs runtime helpers. The known affected names are fields named `hasOwnProperty`, field or oneof names such as `$type` when loaded through protobufjs JSON/reflection descriptors, and service methods whose generated helper name is `rpcCall`.

When affected message or service types were used, protobufjs could read schema-controlled data where it expected an own-property helper, reflected type metadata, or the base RPC helper. This could cause deterministic exceptions or recursive calls in affected decode post-checks, verification, object conversion, reflected JSON serialization, or protobufjs RPC helper invocation.

## Impact

An attacker who can provide or influence protobuf schemas or protobufjs JSON descriptors may be able to make affected message or service types unusable, resulting in denial of service for the affected processing path.

Applications using only trusted schemas are affected only if those schemas contain one of the problematic names and the application reaches the affected API path.

The issue is not known to allow code execution by itself.

## Preconditions

* The application must use an affected protobufjs version.
* The application must load or use a schema or protobufjs JSON descriptor containing one of the problematic names:
  * a field named `hasOwnProperty`,
  * a field or oneof named `$type` through protobufjs JSON/reflection descriptor input,
  * or a service method whose generated helper name is `rpcCall`.
* The application must reach the affected API path for that name: required-field decode post-checks, `verify`, or `toObject` for `hasOwnProperty`; reflected message JSON serialization for `$type`; or protobufjs RPC service invocation for `rpcCall`.

## Workarounds

Do not load protobuf schemas or protobufjs JSON descriptors from untrusted sources with affected versions. If untrusted schemas or descriptors must be accepted, validate schema-derived field, oneof, and service method names before loading and reject the problematic names described above.

Applications using trusted schemas can avoid the issue by renaming affected fields or service methods, or by avoiding the affected API path.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-f38q-mgvj-vph7
- https://nvd.nist.gov/vuln/detail/CVE-2026-54269
- https://github.com/protobufjs/protobuf.js
