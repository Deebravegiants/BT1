# [M] Improper Verification of Cryptographic Signature in aws-encryption-sdk-java

## Summary
Severity: Medium
Advisory: GHSA-55xh-53m6-936r
CVE: CVE-2024-23680
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2021-06-01
Source: https://github.com/advisories/GHSA-55xh-53m6-936r
Type: github-advisory

## Affected
- Maven: `com.amazonaws:aws-encryption-sdk-java` — affected >=0 <1.9.0
- Maven: `com.amazonaws:aws-encryption-sdk-java` — affected >=2.0.0 <2.2.0

## Details
### Impact

This advisory addresses several LOW severity issues with streaming signed messages and restricting processing of certain types of invalid messages. 

This update addresses an issue where certain invalid ECDSA signatures incorrectly passed validation. These signatures provide defense in depth and there is no impact on the integrity of decrypted plaintext.

This ESDK supports a streaming mode where callers may stream the plaintext of signed messages before the ECDSA signature is validated. In addition to these signatures, the ESDK uses AES-GCM encryption and all plaintext is verified before being released to a caller. There is no impact on the integrity of the ciphertext or decrypted plaintext, however some callers may rely on the the ECDSA signature for non-repudiation. Without validating the ECDSA signature, an actor with trusted KMS permissions to decrypt a message may also be able to encrypt messages. This update introduces a new API for callers who wish to stream only unsigned messages. 

For customers who process ESDK messages from untrusted sources, this update also introduces a new configuration to limit the number of Encrypted Data Keys (EDKs) that the ESDK will attempt to process per message. This configuration provides customers with a way to limit the number of AWS KMS Decrypt API calls that the ESDK will make per message. This setting will reject messages with more EDKs than the configured limit.

Finally, this update adds early rejection of invalid messages with certain invalid combinations of algorithm suite and header data.

### Patches

Fixed in versions 1.9 and 2.2. We recommend that all users upgrade to address these issues.

Customers leveraging the ESDK’s streaming features have several options to protect signature validation. One is to ensure that client code reads to the end of the stream before using released plaintext. With this release, using the new API for streaming and falling back to the non-streaming decrypt API for signed messages prevents using any plaintext from signed data before the signature is validated. See https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/about-versions.html#version2.2.x

Users processing ESDK messages from untrusted sources should use the new maximum encrypted data keys parameter. See https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/about-versions.html#version2.2.x

### Workarounds

None

### For more information

https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/concepts.html#digital-sigs

https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/about-versions.html#version2.2.x

## References
- https://github.com/aws/aws-encryption-sdk-java/security/advisories/GHSA-55xh-53m6-936r
- https://nvd.nist.gov/vuln/detail/CVE-2024-23680
- https://github.com/aws/aws-encryption-sdk-java
- https://vulncheck.com/advisories/vc-advisory-GHSA-55xh-53m6-936r
