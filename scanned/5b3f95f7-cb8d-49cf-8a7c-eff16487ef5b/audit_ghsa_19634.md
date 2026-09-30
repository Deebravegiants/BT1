# [M] Wire has Uncontrolled Recursion on Nested Groups

## Summary
Severity: Medium
Advisory: GHSA-pwf9-q62p-v7wc
CVE: CVE-2024-58103
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2025-03-16
Source: https://github.com/advisories/GHSA-pwf9-q62p-v7wc
Type: github-advisory

## Affected
- Maven: `com.squareup.wire:wire-runtime` — affected >=0 <5.2.0

## Details
Square Wire before 5.2.0 does not enforce a recursion limit on nested groups in ByteArrayProtoReader32.kt and ProtoReader.kt.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-58103
- https://github.com/square/wire/commit/b90e60c09befaff836a2fc2ee4d678451b2ec75d
- https://github.com/square/wire
- https://github.com/square/wire/compare/5.1.0...5.2.0
