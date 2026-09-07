# [H] protobuf.js: Process-wide denial of service through unsafe option paths

## Summary
Severity: High
Advisory: GHSA-jvwf-75h9-cwgg
CVE: CVE-2026-44290
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-jvwf-75h9-cwgg
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=0 <7.5.6
- npm: `protobufjs` — affected >=8.0.0 <8.0.2

## Details
## Summary

protobufjs allowed certain schema option paths to traverse through inherited object properties while applying options. A crafted protobuf schema or JSON descriptor could cause option handling to write to properties on global JavaScript constructors, corrupting process-wide built-in functionality.

## Impact

An attacker who can provide or influence protobuf schemas or JSON descriptors may be able to corrupt built-in process state in a way that causes subsequent application code or protobufjs code to fail. This can result in a persistent denial of service for the lifetime of the affected process.

This issue affects applications that parse or load protobuf schemas or descriptors from untrusted sources. Applications that use bundled, generated, or otherwise trusted schemas to decode untrusted protobuf message payloads are not directly affected.

The issue is not known to allow code execution by itself.

## Preconditions

- The application must allow an attacker to control or influence a protobuf schema or JSON descriptor.
- The application must parse or load that schema through protobufjs reflection APIs such as `parse`, `Root.load`, `Root.loadSync`, or `Root.fromJSON`.
- The crafted input must contain option paths that reach unsafe inherited properties during option processing.

## Workarounds

Do not parse or load protobuf schemas or JSON descriptors from untrusted sources with affected versions. If untrusted schemas must be accepted, validate or reject option names containing unsafe property path components before loading them, and run schema processing in an isolated process.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-jvwf-75h9-cwgg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44290
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v7.5.6
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v8.0.2
