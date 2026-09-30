# [H] ALPINE-CVE-2025-23166

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-23166
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-23166
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.15.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.16.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <22.16.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <22.16.0-r0

## Details
The C++ method SignTraits::DeriveBits() may incorrectly call ThrowException() based on user-supplied inputs when executing in a background thread, crashing the Node.js process. Such cryptographic operations are commonly applied to untrusted inputs. Thus, this mechanism potentially allows an adversary to remotely crash a Node.js runtime.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-23166
