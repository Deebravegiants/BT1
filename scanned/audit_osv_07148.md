# [H] BIT-node-2023-46809

## Summary
Severity: High
Advisory: BIT-node-2023-46809
Aliases: BIT-node-min-2023-46809, CVE-2023-46809
Ecosystem: Bitnami
Published: 2024-09-11
Source: https://osv.dev/vulnerability/BIT-node-2023-46809
Type: osv

## Affected
- Bitnami: `node` — affected >=21.0.0 <21.6.1

## Details
Node.js versions which bundle an unpatched version of OpenSSL or run against a dynamically linked version of OpenSSL which are unpatched are vulnerable to the Marvin Attack - https://people.redhat.com/~hkario/marvin/, if PCKS #1 v1.5 padding is allowed when performing RSA descryption using a private key.

## References
- https://nodejs.org/en/blog/vulnerability/february-2024-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2023-46809
- https://lists.debian.org/debian-lts-announce/2024/03/msg00029.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00029.html
