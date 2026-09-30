# [C] Arbitrary code execution in protobufjs

## Summary
Severity: Critical
Advisory: GHSA-xq3m-2v4x-88gg
CVE: CVE-2026-41242
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-xq3m-2v4x-88gg
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=8.0.0 <8.0.1
- npm: `protobufjs` — affected >=0 <7.5.5

## Details
## Summary

protobufjs could execute generated JavaScript code derived from protobuf schema metadata. When loading a crafted JSON descriptor, schema-controlled type names and type references could reach runtime code generation without sufficient validation.

## Impact

An attacker who can provide a malicious protobuf definition or JSON descriptor to an application may be able to execute arbitrary JavaScript in the context of the process using protobufjs.

This requires control over the protobuf schema or descriptor being loaded. Applications that only decode messages using trusted, application-defined schemas are not directly affected by this issue.

## Preconditions

- The application must allow an attacker to control or influence a protobuf definition or JSON descriptor.
- The application must load that definition through protobufjs reflection APIs such as descriptor loading.
- The affected generated-code path must be reached, for example by performing an operation on the loaded type.

## Workarounds

Do not load protobuf definitions or JSON descriptors from untrusted sources with affected versions. If untrusted schemas must be accepted, validate or restrict them before loading and run schema processing in an isolated environment.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-xq3m-2v4x-88gg
- https://nvd.nist.gov/vuln/detail/CVE-2026-41242
- https://github.com/protobufjs/protobuf.js/commit/535df444ac060243722ac5d672db205e5c531d75
- https://github.com/protobufjs/protobuf.js/commit/ff7b2afef8754837cc6dc64c864cd111ab477956
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v7.5.5
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v8.0.1
