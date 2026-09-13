# [M] ConnectBot SSH Client Library: Excessive allocation and integer overflow in DER private-key parsing

## Summary
Severity: Medium
Advisory: GHSA-vc8p-8pxg-rfwg
CVE: CVE-2026-54697
CWE: CWE-190, CWE-789
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-vc8p-8pxg-rfwg
Type: github-advisory

## Affected
- Maven: `org.connectbot.sshlib:sshlib` — affected >=0

## Details
## Summary

The DER parser used for application-supplied private keys did not safely validate encoded length values before converting them to `Int` values or allocating arrays.

A malformed private-key file could encode a length that overflowed or wrapped around, or request an allocation much larger than the available input. This could cause parsing errors or an uncaught `OutOfMemoryError`, potentially terminating the application process.

## Details

The issue was in `DerReader.readLength()` and primitive readers such as `readInteger()`.

`readLength()` previously accepted up to 127 length octets and accumulated them into an `Int`:

```kotlin
length = (length shl 8) or nextByte
```

This permitted integer overflow. For example:

- `0x1_0000_0001` wrapped to `1`.
- `0x8000_0000` wrapped to `Int.MIN_VALUE`.

Primitive readers then allocated memory based on the resulting value without first checking it against the remaining input:

```kotlin
val bytes = ByteArray(length)
data.get(bytes)
```

A six-byte DER value declaring a 1 GiB INTEGER caused an immediate `OutOfMemoryError` when tested with a constrained JVM heap. Because `OutOfMemoryError` is not an `Exception`, it is not caught by the public-key authentication error handling and may terminate the application process.

A zero-length DER INTEGER is also invalid, but it does not produce `BigInteger.ZERO`: Java throws `NumberFormatException` when constructing a `BigInteger` from an empty byte array. No weakened or usable cryptographic key has been demonstrated through this issue.

## Attack Requirements

The affected DER parser processes private-key material explicitly supplied by the application through APIs such as:

- `SshClient.authenticatePublicKey()`
- `SshKeys.decodePemPrivateKey()`
- `SshSigning.sign()`
- `SshSigning.getPublicKey()`

The DER input is not populated from SSH server host keys or agent-forwarding requests. Exploitation therefore requires a user or application to load an attacker-provided private-key file. The issue is not remotely exploitable by an SSH server.

## Impact

Successful exploitation can cause:

- Incorrect DER length interpretation due to integer wraparound
- Excessive memory allocation
- An uncaught `OutOfMemoryError`
- Loss of availability of the affected application process

There is no demonstrated confidentiality or integrity impact.

## Remediation

The DER parser now:

- Rejects indefinite lengths
- Explicitly limits long-form lengths to `Int.SIZE_BYTES` (four octets) and rejects values above `Int.MAX_VALUE`
- Accumulates long-form lengths in a `Long` before converting to `Int`
- Rejects truncated and non-minimal length encodings
- Checks declared lengths against the remaining input before allocation or advancing the input position
- Rejects zero-length DER INTEGER, BIT STRING, and OBJECT IDENTIFIER values where an empty encoding is invalid
- Rejects non-canonical DER INTEGER encodings with redundant sign octets

The bounds checks are implemented in shared DER reader helpers and apply to INTEGER, OCTET STRING, BIT STRING, OBJECT IDENTIFIER, SEQUENCE, context-specific values, and skipped values. PKCS#1 RSA and SEC1 EC private keys pass application-supplied DER directly through these helpers. PKCS#8 input is parsed by the JCA provider, and OpenSSH private keys use a separate wire-format parser rather than `DerReader`.

## References
- https://github.com/connectbot/cbssh/security/advisories/GHSA-vc8p-8pxg-rfwg
- https://github.com/connectbot/cbssh
- https://github.com/connectbot/cbssh/releases/tag/v0.3.1
