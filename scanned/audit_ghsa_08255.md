# [H] protobuf.js: Code injection through bytes field defaults in generated toObject code

## Summary
Severity: High
Advisory: GHSA-66ff-xgx4-vchm
CVE: CVE-2026-44293
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-66ff-xgx4-vchm
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=0 <7.5.6
- npm: `protobufjs` — affected >=8.0.0 <8.0.2

## Details
## Summary

protobufjs generated JavaScript for `toObject` conversion could include an unsafe expression derived from a schema-controlled `bytes` field default value. A crafted descriptor with a non-string default value for a `bytes` field could cause attacker-controlled code to be emitted into the generated conversion function.

## Impact

An attacker who can provide or influence a protobuf descriptor may be able to execute arbitrary JavaScript in the context of the process using protobufjs.

This requires the application to load an attacker-controlled schema or descriptor and then convert a message of the affected type with defaults enabled. Applications that only use trusted, application-defined schemas are not directly affected by this issue.

## Preconditions

- The application must allow an attacker to control or influence a protobuf JSON descriptor or equivalent reflected schema.
- The descriptor must define a `bytes` field with an attacker-controlled default value.
- The application must call `toObject` with defaults enabled for the affected type.

## Workarounds

Do not load protobuf schemas or JSON descriptors from untrusted sources with affected versions. If untrusted schemas must be accepted, validate or restrict field options before loading them and run schema processing in an isolated environment.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-66ff-xgx4-vchm
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v7.5.6
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v8.0.2
