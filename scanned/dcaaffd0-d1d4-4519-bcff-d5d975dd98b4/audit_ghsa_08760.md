# [H] protobuf.js: Code injection in pbjs static output from crafted schema names

## Summary
Severity: High
Advisory: GHSA-6r35-46g8-jcw9
CVE: CVE-2026-44295
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-6r35-46g8-jcw9
Type: github-advisory

## Affected
- npm: `protobufjs-cli` — affected >=0 <1.2.1
- npm: `protobufjs-cli` — affected >=2.0.0 <2.0.2

## Details
## Summary

`pbjs` static code generation could emit unsafe JavaScript identifiers derived from schema-controlled names. When generating static JavaScript from a crafted schema or JSON descriptor, certain namespace, enum, service, or derived full names could be written into the generated output without sufficient sanitization.

## Impact

An attacker who can provide or influence schemas passed to `pbjs` may be able to cause generated JavaScript output to contain attacker-controlled code. The injected code would run if the generated file is later executed or imported by the application or build process.

This affects the protobufjs CLI static code generation path. Applications that only use trusted schemas, or that do not execute generated output from untrusted schemas, are not directly affected.

## Preconditions

- The application or build process must run `pbjs` static code generation on a schema or JSON descriptor influenced by an attacker.
- The attacker-controlled input must contain crafted schema names that reach generated JavaScript output.
- The generated JavaScript file must subsequently be executed, imported, or otherwise evaluated.

## Workarounds

Do not run affected versions of `pbjs` static code generation on untrusted schemas or descriptors. If untrusted schemas must be accepted, validate schema names before code generation and run generation in an isolated environment.

## References
- https://github.com/protobufjs/protobuf.js/security/advisories/GHSA-6r35-46g8-jcw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44295
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-cli-v1.2.1
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-cli-v2.0.2
