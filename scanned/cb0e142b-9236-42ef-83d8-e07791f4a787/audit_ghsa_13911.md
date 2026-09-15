# [M] Privilege escalation in Strongbox

## Summary
Severity: Medium
Advisory: GHSA-mhgm-52vg-pvvc
CWE: CWE-269
Ecosystem: Maven
Published: 2023-02-16
Source: https://github.com/advisories/GHSA-mhgm-52vg-pvvc
Type: github-advisory

## Affected
- Maven: `com.schibsted.security:strongbox-sdk` — affected >=0 <0.5.0

## Details
### Impact
An attacker with read-only access to a Strongbox secret could craft a valid encrypted secret (same id/version). It also makes the audit logs from KMS less useful. The issue is caused by a bug in the underlying AWS Encryption SDK.

By default, the encrypted secrets are stored in DynamoDB and an attacker with read-only access would not be able to write the encrypted secret to DynamoDB. So in practice the impact should be limited for most users.

Strongbox supports storing data in files as an alternative to DynamoDB. If the attacker had write access to where the files are stored they could make the attack work end-to-end. Similarly, any custom storage backend could also be affected.

In order to be backwards compatible Strongbox will not make use of key commitments (another improvement to the AWS Encryption SDK). Strongbox enforces that only one KMS key can be used, and it must match the expected one. This means that an attacker needs write access to both KMS and DynamoDB (or other storage backend) to stage an attack, which is not a scenario Strongbox is designed to protect against.

### Patches
Fixed in version 0.5.0.

### Workarounds
None

### References
- https://github.com/aws/aws-encryption-sdk-java/security/advisories/GHSA-55xh-53m6-936r
- https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/concepts.html#key-commitment

## References
- https://github.com/schibsted/strongbox/security/advisories/GHSA-mhgm-52vg-pvvc
- https://github.com/schibsted/strongbox/commit/e61f7c36efa898e8b44de6222cd66d2bcdd073e6
- https://github.com/schibsted/strongbox
