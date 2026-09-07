# [H] netty-incubator-codec-ohttp: BoringSSL HPKE private key bytes exposed through toString() and exception messages

## Summary
Severity: High
Advisory: GHSA-2mc4-j865-9q4r
CVE: CVE-2026-61798
CWE: CWE-200, CWE-312, CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-2mc4-j865-9q4r
Type: github-advisory

## Affected
- Maven: `io.netty.incubator:netty-incubator-codec-ohttp-hpke-classes-boringssl` — affected >=0 <0.0.23.Final

## Details
## Summary

`io.netty.incubator:netty-incubator-codec-ohttp-hpke-classes-boringssl` exposes raw HPKE private key bytes in string representations and error messages. `BoringSSLAsymmetricCipherKeyPair.toString()` includes the private-key parameter object, and `BoringSSLAsymmetricKeyParameter.toString()` renders the full byte array with `Arrays.toString(bytes)`. Separately, failed native key initialization includes `Arrays.toString(privateKeyBytes)` in the thrown `IllegalArgumentException` message. Applications that log key-pair objects or exceptions can persist private key material in logs.

## Details

`codec-ohttp-hpke-classes-boringssl/src/main/java/io/netty/incubator/codec/hpke/boringssl/BoringSSLAsymmetricCipherKeyPair.java` renders private key material through `toString()`:

- `BoringSSLAsymmetricCipherKeyPair.toString()` at lines 72-78 concatenates `"privateKey=" + privateKey`.
- `privateKey` is a `BoringSSLAsymmetricKeyParameter` created with `isPrivate=true` at lines 26-36.

`codec-ohttp-hpke-classes-boringssl/src/main/java/io/netty/incubator/codec/hpke/boringssl/BoringSSLAsymmetricKeyParameter.java` then renders all bytes:

- `BoringSSLAsymmetricKeyParameter.toString()` at lines 70-76 returns `"bytes=" + Arrays.toString(bytes)` regardless of whether `isPrivate` is true.

A separate error path in `codec-ohttp-hpke-classes-boringssl/src/main/java/io/netty/incubator/codec/hpke/boringssl/BoringSSL.java` also exposes caller-provided private key bytes:

- `EVP_HPKE_KEY_init_or_throw(...)` at lines 228-232 throws `IllegalArgumentException("privateKeyBytes does not contain a valid private key: " + Arrays.toString(privateKeyBytes))` when BoringSSL rejects the key.

Because Java logging frameworks commonly call `toString()` for structured objects and commonly persist exception messages, these paths can place complete HPKE private key material in logs or telemetry.

## Proof of concept

Safe local verification was performed without native BoringSSL by compiling the relevant Java classes and a no-op native stub for the unused finalizer reference. The observed output includes the full private key byte array:

```text
BoringSSLAsymmetricCipherKeyPair{privateKey=BoringSSLAsymmetricKeyParameter{bytes=[1, 2, 3, 4], isPrivate=true}, publicKey=BoringSSLAsymmetricKeyParameter{bytes=[5, 6, 7, 8], isPrivate=false}}
```

Minimal reproducer concept in the same package:

```java
package io.netty.incubator.codec.hpke.boringssl;

public final class VerifyPrivateKeyToString {
  public static void main(String[] args) {
    byte[] privateKey = new byte[] {1, 2, 3, 4};
    byte[] publicKey = new byte[] {5, 6, 7, 8};
    BoringSSLAsymmetricCipherKeyPair pair = new BoringSSLAsymmetricCipherKeyPair(privateKey, publicKey);
    System.out.println(pair.toString());
  }
}
```

The code path is deterministic: the production `toString()` methods concatenate the raw private-key byte array.

## Impact

If an affected key pair or initialization exception is logged, application logs contain complete HPKE private key material. Anyone with access to those logs can recover the key. Depending on key reuse and log retention, this can compromise:

- confidentiality of OHTTP messages encrypted to the exposed key;
- integrity/authenticity expectations for future messages if the key remains active;
- incident response and key rotation assumptions, because logs may retain key material long after the in-memory key is rotated.

## Suggested remediation

- Redact private key material in `BoringSSLAsymmetricKeyParameter.toString()` when `isPrivate` is true, for example `bytes=<redacted>` or only key type/length.
- Redact `privateKey` in `BoringSSLAsymmetricCipherKeyPair.toString()`.
- Remove `Arrays.toString(privateKeyBytes)` from `BoringSSL.EVP_HPKE_KEY_init_or_throw(...)`; report only length and KEM metadata.
- Add regression tests asserting that `toString()` and exception messages do not contain private key byte values.
- Consider making key pair classes avoid implementing detailed `toString()` for sensitive material entirely.

## References

- `codec-ohttp-hpke-classes-boringssl/src/main/java/io/netty/incubator/codec/hpke/boringssl/BoringSSLAsymmetricCipherKeyPair.java:72-78`
- `codec-ohttp-hpke-classes-boringssl/src/main/java/io/netty/incubator/codec/hpke/boringssl/BoringSSLAsymmetricKeyParameter.java:70-76`
- `codec-ohttp-hpke-classes-boringssl/src/main/java/io/netty/incubator/codec/hpke/boringssl/BoringSSL.java:228-232`

## References
- https://github.com/netty/netty-incubator-codec-ohttp/security/advisories/GHSA-2mc4-j865-9q4r
- https://github.com/netty/netty-incubator-codec-ohttp
- https://github.com/netty/netty-incubator-codec-ohttp/releases/tag/netty-incubator-codec-parent-ohttp-0.0.23.Final
