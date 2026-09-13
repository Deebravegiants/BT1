# [M] protobuf.js: Prototype injection in generated message constructors

## Summary
Severity: Medium
Advisory: GHSA-fx83-v9x8-x52w
CVE: CVE-2026-44292
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-fx83-v9x8-x52w
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=0 <7.5.6
- npm: `protobufjs` — affected >=8.0.0 <8.0.2

## Details
## Summary

protobufjs generated message constructors copied enumerable properties from a provided properties object without filtering the `__proto__` key. If an application constructed a message from an attacker-controlled plain object, an own enumerable `__proto__` property could alter the prototype of that individual message instance.

## Impact

An attacker who can control the properties object passed to a generated protobufjs message constructor or creation helper may be able to modify the prototype chain of the resulting message instance.

This is a per-instance prototype injection issue. It does not pollute `Object.prototype` or other global prototypes. The impact depends on downstream application behavior, such as relying on inherited properties, prototype methods, or `instanceof` checks for message objects.

Applications that only decode binary protobuf data, or that construct messages from trusted application-defined objects, are not directly affected by this issue.

## Preconditions

- The application must allow an attacker to control or influence a plain object used to construct a protobufjs message.
- The object must contain an own enumerable `__proto__` property, for example from parsed JSON input.
- The application must pass that object to a generated message constructor or creation helper that copies arbitrary enumerable properties.

## Workarounds

Do not pass attacker-controlled plain objects directly to generated message constructors with affected versions. If untrusted JSON input must be accepted, validate or sanitize object keys before constructing messages, and reject `__proto__` properties.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-fx83-v9x8-x52w
- https://nvd.nist.gov/vuln/detail/CVE-2026-44292
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v7.5.6
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v8.0.2
