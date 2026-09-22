# [M] protobufjs has overlong UTF-8 decoding

## Summary
Severity: Medium
Advisory: GHSA-q6x5-8v7m-xcrf
CVE: CVE-2026-44288
CWE: CWE-176
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-q6x5-8v7m-xcrf
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=0 <7.5.6
- npm: `protobufjs` — affected >=8.0.0 <8.0.2
- npm: `@protobufjs/utf8` — affected >=0 <1.1.1

## Details
## Summary

protobufjs includes a minimal UTF-8 decoder used in non-Node and fallback decoding paths. The affected decoder accepted overlong UTF-8 byte sequences and decoded them to their canonical characters instead of replacing them.

The issue concerns overlong encodings and code points outside the Unicode range. protobufjs may still accept some non-strict UTF-8 input for compatibility, so applications should not rely on protobufjs as a general-purpose strict UTF-8 validator.

## Impact

An attacker who can provide protobuf binary data decoded through the affected UTF-8 path may be able to bypass application-level checks that inspect raw bytes before protobuf string decoding. For example, bytes that do not contain certain ASCII characters could decode to strings containing those characters.

The practical impact depends on downstream application validation and how decoded strings are used. Node.js Buffer-backed decoding paths are not directly affected when they use Node's native UTF-8 decoding.

## Preconditions

- The application must decode protobuf binary data influenced by an attacker.
- The affected protobuf string field must be decoded through protobufjs's minimal UTF-8 decoder rather than a native UTF-8 decoder.
- The application must rely on byte-level filtering or validation before protobuf string decoding.
- The decoded string must then be used in a security-sensitive context.

## Workarounds

Avoid relying only on byte-level filtering before protobuf string decoding with affected versions. Validate decoded strings at the point where they are used, and prefer runtime paths that use native UTF-8 decoding where necessary.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-q6x5-8v7m-xcrf
- https://nvd.nist.gov/vuln/detail/CVE-2026-44288
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v7.5.6
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v8.0.2
