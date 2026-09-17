# [H] ALPINE-CVE-2019-12083

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12083
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12083
Type: osv

## Affected
- Alpine:v3.19: `rust` — affected >=1.34.0 <1.34.2-r0
- Alpine:v3.20: `rust` — affected >=1.34.0 <1.34.2-r0
- Alpine:v3.21: `rust` — affected >=1.34.0 <1.34.2-r0
- Alpine:v3.22: `rust` — affected >=1.34.0 <1.34.2-r0
- Alpine:v3.23: `rust` — affected >=1.34.0 <1.34.2-r0
- Alpine:v3.24: `rust` — affected >=1.34.0 <1.34.2-r0

## Details
The Rust Programming Language Standard Library 1.34.x before 1.34.2 contains a stabilized method which, if overridden, can violate Rust's safety guarantees and cause memory unsafety. If the `Error::type_id` method is overridden then any type can be safely cast to any other type, causing memory safety vulnerabilities in safe code (e.g., out-of-bounds write or read). Code that does not manually implement Error::type_id is unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12083
