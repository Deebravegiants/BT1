# [M] protobufjs: Memory amplification from preserved unknown fields in binary decode

## Summary
Severity: Medium
Advisory: GHSA-94rc-8x27-4472
CVE: CVE-2026-54270
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-94rc-8x27-4472
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=8.2.0 <8.5.0

## Details
## Summary

protobufjs 8.2.0 added support for preserving unknown fields encountered during binary decode. Affected versions preserved unknown wire elements in `message.$unknowns` and did not provide a decode-time option to discard unknown fields before retaining them.

A crafted protobuf payload containing many unknown fields could therefore cause a decoded message to retain substantially more memory than the input size would suggest, even when unknown-field round-tripping is not needed. protobufjs 8.5.0 added the relevant decode-time options, allowing applications that decode untrusted protobuf data to disable unknown-field retention during decode. protobufjs 8.6.2 flips the default so unknown fields are discarded unless explicitly opted into.

## Impact

An attacker who can provide protobuf binary data decoded by an application using affected protobufjs versions may be able to increase memory pressure by sending messages with many unknown fields. This can degrade availability or contribute to process termination in services that decode and retain attacker-controlled messages.

This issue affects applications that decode untrusted protobuf binary input and do not need unknown-field round-tripping. Applications that only decode trusted protobuf data, already enforce input-size/concurrency limits, or do not retain decoded messages beyond immediate processing are less directly affected.

## Preconditions

* The application must decode protobuf binary data influenced by an attacker.
* The decoded schema must not define the attacker-selected field numbers, causing those fields to be treated as unknown.
* The application must use a protobufjs version that preserves unknown fields but does not provide a decode-time discard option.
* The decoded message, or enough decoded messages concurrently, must remain live long enough for retained unknown-field data to affect memory usage.

## Workarounds

Upgrade to protobufjs 8.5.0 or newer and disable unknown-field preservation if not needed: Create a `Reader`, set `reader.discardUnknown = true`, and decode from that reader, or make this the default for subsequently created readers by setting `Reader.discardUnknown = true`. When upgrading to protobufjs 8.6.2 or newer, unknown fields are discarded by default unless opted into by setting `discardUnknown = false`.

Applications should also continue to enforce input-size, request concurrency, and request timeout limits at their transport or application boundary.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-94rc-8x27-4472
- https://nvd.nist.gov/vuln/detail/CVE-2026-54270
- https://github.com/protobufjs/protobuf.js
