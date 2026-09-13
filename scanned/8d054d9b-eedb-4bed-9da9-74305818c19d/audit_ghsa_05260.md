# [H] protobufjs-cli: Code injection in pbjs static output from crafted JSON descriptor names

## Summary
Severity: High
Advisory: GHSA-pr59-h9ph-3fr8
CVE: CVE-2026-54271
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-pr59-h9ph-3fr8
Type: github-advisory

## Affected
- npm: `protobufjs-cli` — affected >=0 <1.3.2
- npm: `protobufjs-cli` — affected >=2.0.0 <2.5.0

## Details
## Summary

A previous fix for unsafe name handling in `pbjs` static / static-module code generation was incomplete. Affected versions of `protobufjs-cli` could still emit unsafe JavaScript references when generating static output from crafted JSON descriptor input. The common case of parsing schemas from `.proto` files is not affected.

This is a bypass of GHSA-6r35-46g8-jcw9 / CVE-2026-44295.

## Impact

An attacker who can provide or influence pre-parsed JSON descriptors passed to `pbjs` static code generation may be able to cause generated JavaScript output to contain attacker-controlled code.

The injected code may execute if the generated file is later executed or imported and an affected generated API path is invoked.

## Preconditions

* The application or build process must run `pbjs` static code generation on a pre-parsed JSON descriptor influenced by an attacker.
* The generated JavaScript file must subsequently be executed or imported.
* An affected generated API path must be invoked.

## Workarounds

Do not run affected versions of `pbjs` static or static-module generation on untrusted JSON descriptors. If untrusted JSON descriptors must be accepted, validate descriptor-derived names before code generation and reject names that could not have been produced by parsing a valid `.proto` file. Running code generation in an isolated environment can reduce impact.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-pr59-h9ph-3fr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-54271
- https://github.com/protobufjs/protobuf.js
