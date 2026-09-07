# [M] russh may use insecure Diffie-Hellman keys

## Summary
Severity: Medium
Advisory: GHSA-cqvm-j2r2-hwpg
CVE: CVE-2023-28113
CWE: CWE-20, CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-17
Source: https://github.com/advisories/GHSA-cqvm-j2r2-hwpg
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0 <0.36.2
- crates.io: `russh` — affected >=0.37.0 <0.37.1

## Details
### Summary

Diffie-Hellman key validation is insufficient, which can lead to insecure shared secrets and therefore breaks confidentiality.

### Details

Russh does not validate Diffie-Hellman keys.

It accepts received DH public keys $e$ where $e<0$, $e=1$, or $e \geq p-1$ from a misbehaving peer annd successfully performs key exchange.

This is a violation of [RFC 4253, section 8](https://www.rfc-editor.org/rfc/rfc4253#section-8) and [RFC 8268, section 4](https://www.rfc-editor.org/rfc/rfc8268#section-4), which state that:

>DH Public Key values MUST be checked and both conditions:
>
> - $1 < e < p-1$
> - $1 < f < p-1$
>
> MUST be true.  Values not within these bounds MUST NOT be sent or
> accepted by either side.  If either one of these conditions is
> violated, then the key exchange fails.

For example, a DH client public key $e=1$ would mean that the shared secret that the server calculates is always $K = e^y \mod{p} = 1^y \mod{p} = 1$.
In other cases, an insecure order-2 subgroup may be used.

Also, the code does not look like it ensures that the generated secret key $y$ is in the valid interval $0 < y < q$ (or, if russh is the client, that the secret key $x$ satisfies $1 < x < q$):
https://github.com/warp-tech/russh/blob/master/russh/src/kex/dh/groups.rs#L72-L76
For example, `rng.gen_biguint()` might return a number consisting of zeroes, so that $y = 0$.

The public key is not validated either:
https://github.com/warp-tech/russh/blob/master/russh/src/kex/dh/groups.rs#L78-L81

### Impact

Due to the issues in the DH key generation, I think any connection that uses Diffie-Hellman key exchange is affected.
Connections between a russh client and server or those of a russh peer with some other misbehaving peer are most likely to be problematic. These may vulnerable to eavesdropping.

Most other implementations reject such keys, so this is mainly an interoperability issue in such a case.

## References
- https://github.com/warp-tech/russh/security/advisories/GHSA-cqvm-j2r2-hwpg
- https://nvd.nist.gov/vuln/detail/CVE-2023-28113
- https://github.com/warp-tech/russh/commit/45d2d82930bf4a675bd57abfafec8fe4065befcd
- https://github.com/warp-tech/russh/commit/d831a3716d3719dc76f091fcea9d94bd4ef97c6e
- https://github.com/warp-tech/russh
- https://github.com/warp-tech/russh/blob/master/russh/src/kex/dh/groups.rs#L72-L76
- https://github.com/warp-tech/russh/blob/master/russh/src/kex/dh/groups.rs#L78-L81
- https://github.com/warp-tech/russh/releases/tag/v0.36.2
- https://github.com/warp-tech/russh/releases/tag/v0.37.1
