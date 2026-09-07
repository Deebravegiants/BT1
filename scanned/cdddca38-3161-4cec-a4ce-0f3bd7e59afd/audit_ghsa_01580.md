# [M] Ciphertext Malleability Issue in Tink Java

## Summary
Severity: Medium
Advisory: GHSA-g5vf-v6wf-7w2r
CVE: CVE-2020-8929
CWE: CWE-176, CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-10-16
Source: https://github.com/advisories/GHSA-g5vf-v6wf-7w2r
Type: github-advisory

## Affected
- Maven: `com.google.crypto.tink:tink` — affected >=0 <1.5.0

## Details
### Impact
Tink's Java version before 1.5 under some circumstances allowed attackers to change the key ID part of the ciphertext, resulting in the attacker creating a second ciphertext that will decrypt to the same plaintext. This can be a problem in particular in the case of encrypting with a deterministic AEAD with a single key, and relying on the fact that there is only a single valid ciphertext per plaintext.

No loss of confidentiality or loss of plaintext integrity occurs due to this problem, only ciphertext integrity is compromised.

### Patches
The issue was fixed in this [pull request](https://github.com/google/tink/commit/93d839a5865b9d950dffdc9d0bc99b71280a8899).

### Workarounds
The only workaround is to backport the fixing [pull request](https://github.com/google/tink/commit/93d839a5865b9d950dffdc9d0bc99b71280a8899).

### Details
Tink uses the first five bytes of a ciphertext for a version byte and a four byte key ID. Since each key has a well defined prefix, this extends non-malleability properties (but technically not indistinguishability). However, in the Java version this prefix lookup used a hash map indexed by unicode strings instead of the byte array, which means that invalid Unicode characters would be [replaced by U+FFFD](https://en.wikipedia.org/wiki/UTF-8#Invalid_sequences_and_error_handling) by the [Java API's default behavior](https://docs.oracle.com/javase/7/docs/api/java/lang/String.html#String(byte[],%20java.nio.charset.Charset)). This means several different values for the five bytes would result in the same hash table key, which allows an attacker to exchange one invalid byte sequence for another, creating a mutated ciphertext that still decrypts (to the same plaintext).

### Acknowledgements
We'd like to thank Peter Esbensen for finding this issue and raising it internally.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Tink](https://github.com/google/tink/issues)

## References
- https://github.com/google/tink/security/advisories/GHSA-g5vf-v6wf-7w2r
- https://nvd.nist.gov/vuln/detail/CVE-2020-8929
- https://github.com/google/tink/commit/93d839a5865b9d950dffdc9d0bc99b71280a8899
- https://github.com/pypa/advisory-database/tree/main/vulns/tink/PYSEC-2020-142.yaml
