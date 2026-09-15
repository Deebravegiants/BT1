# [H] BIT-node-2025-23166

## Summary
Severity: High
Advisory: BIT-node-2025-23166
Aliases: BIT-node-min-2025-23166, CVE-2025-23166
Ecosystem: Bitnami
Published: 2025-05-21
Source: https://osv.dev/vulnerability/BIT-node-2025-23166
Type: osv

## Affected
- Bitnami: `node` — affected >=23.0.0 <24.0.2

## Details
The C++ method SignTraits::DeriveBits() may incorrectly call ThrowException() based on user-supplied inputs when executing in a background thread, crashing the Node.js process. Such cryptographic operations are commonly applied to untrusted inputs. Thus, this mechanism potentially allows an adversary to remotely crash a Node.js runtime.

## References
- https://nodejs.org/en/blog/vulnerability/may-2025-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-23166
