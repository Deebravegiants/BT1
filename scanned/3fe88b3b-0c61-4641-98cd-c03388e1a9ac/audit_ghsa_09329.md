# [H] protobuf.js: Code generation gadget after prototype pollution

## Summary
Severity: High
Advisory: GHSA-75px-5xx7-5xc7
CVE: CVE-2026-44291
CWE: CWE-1321, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-75px-5xx7-5xc7
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=0 <7.5.6
- npm: `protobufjs` — affected >=8.0.0 <8.0.2

## Details
## Summary

protobufjs used plain objects with inherited prototypes for internal type lookup tables used by generated encode and decode functions. If `Object.prototype` had already been polluted, those lookup tables could resolve attacker-controlled inherited properties as valid protobuf type information.

This could cause attacker-controlled strings to be emitted into generated JavaScript code.

## Impact

An attacker who can first trigger a prototype pollution vulnerability may be able to influence generated protobufjs encode or decode functions in a way that can lead to arbitrary JavaScript execution.

This issue requires a separate prototype pollution primitive before protobufjs is invoked.

Applications without a reachable prototype pollution primitive are not directly exploitable through this issue alone.

## Preconditions

- The application or one of its dependencies must allow an attacker to pollute `Object.prototype`.
- The polluted property must affect protobufjs internal type lookup behavior.
- The application must use protobufjs functionality that generates encode or decode code for affected types.
- The generated code path must be reached after the prototype pollution has occurred.

## Workarounds

Avoid running affected versions in applications where attacker-controlled input can pollute `Object.prototype`. If immediate upgrade is not possible, remove or mitigate reachable prototype pollution primitives and isolate schema/message processing from untrusted application state.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-75px-5xx7-5xc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44291
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v7.5.6
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v8.0.2
