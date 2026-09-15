# [H] protobufjs: Denial of service through unbounded Any expansion during JSON conversion

## Summary
Severity: High
Advisory: GHSA-wcpc-wj8m-hjx6
CVE: CVE-2026-48712
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-wcpc-wj8m-hjx6
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=0 <7.6.1
- npm: `protobufjs` — affected >=8.0.0 <8.4.1

## Details
## Summary

protobufjs could recurse without a depth limit while converting decoded messages to plain objects or JSON. This affected generated `toObject()` conversion and the custom `google.protobuf.Any` JSON conversion path.

A crafted protobuf binary payload containing deeply nested `Any` values could cause the JavaScript call stack to be exhausted during conversion to JSON.

## Impact

An attacker who can provide protobuf binary data decoded by an application may be able to crash the process or otherwise cause message conversion to fail with a stack overflow.

This affects applications that decode untrusted protobuf input containing `google.protobuf.Any` values and then convert decoded messages to JSON or plain objects with JSON conversion enabled, for example through `JSON.stringify(message)`, `Message#toJSON()`, or `Type.toObject(message, { json: true })`.

Applications that only decode and re-encode protobuf binary data without converting decoded messages to JSON are not directly affected by this issue.

## Preconditions

* The application must decode protobuf binary data influenced by an attacker.
* The application schema must include `google.protobuf.Any`, and the referenced `type_url` must resolve to a message type in the loaded protobuf root.
* The application must convert the decoded message to JSON or a plain object through an affected conversion path.
* The crafted input must contain deeply nested `Any` values that are expanded during conversion.

## Workarounds

Avoid converting untrusted protobuf messages containing `google.protobuf.Any` values to JSON with affected versions. If immediate upgrade is not possible, reject or limit messages with deeply nested `Any` payloads at an outer protocol boundary where feasible, avoid JSON conversion of untrusted `Any` values, or isolate message conversion in a process that can be safely restarted.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-wcpc-wj8m-hjx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-48712
- https://github.com/protobufjs/protobuf.js
