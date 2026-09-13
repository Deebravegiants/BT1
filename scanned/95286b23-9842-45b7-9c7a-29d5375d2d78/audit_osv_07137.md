# [H] BIT-node-2023-30590

## Summary
Severity: High
Advisory: BIT-node-2023-30590
Aliases: BIT-node-min-2023-30590, CVE-2023-30590
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-30590
Type: osv

## Affected
- Bitnami: `node` — affected >=20.0.0 <20.3.1

## Details
The generateKeys() API function returned from crypto.createDiffieHellman() only generates missing (or outdated) keys, that is, it only generates a private key if none has been set yet, but the function is also needed to compute the corresponding public key after calling setPrivateKey(). However, the documentation says this API call: "Generates private and public Diffie-Hellman key values".

The documented behavior is very different from the actual behavior, and this difference could easily lead to security issues in applications that use these APIs as the DiffieHellman may be used as the basis for application-level security, implications are consequently broad.

## References
- https://nodejs.org/en/blog/vulnerability/june-2023-security-releases
- https://lists.debian.org/debian-lts-announce/2024/03/msg00029.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-30590
- https://lists.debian.org/debian-lts-announce/2024/09/msg00029.html
- https://security.netapp.com/advisory/ntap-20241101-0011/
