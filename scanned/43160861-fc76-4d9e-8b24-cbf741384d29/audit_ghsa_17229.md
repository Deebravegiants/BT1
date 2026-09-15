# [M] AWS SDK for PHP's S3 Encryption Client has a Key Commitment Issue

## Summary
Severity: Medium
Advisory: GHSA-x8cp-jf6f-r4xh
CVE: CVE-2025-14761
CWE: CWE-327
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-12-18
Source: https://github.com/advisories/GHSA-x8cp-jf6f-r4xh
Type: github-advisory

## Affected
- Packagist: `aws/aws-sdk-php` — affected >=0 <3.368.0

## Details
## Summary

S3 Encryption Client for PHP is an open-source client-side encryption library used to facilitate writing and reading encrypted records to S3.  

When the encrypted data key (EDK) is stored in an "Instruction File" instead of S3's metadata record, the EDK is exposed to an "Invisible Salamanders" attack  (https://eprint.iacr.org/2019/016), which could allow the EDK to be replaced with a new key. 



## Impact

### Background - Key Commitment

There is a cryptographic property whereby under certain conditions, a single ciphertext can be decrypted into 2 different plaintexts by using different encryption keys. To address this issue, strong encryption schemes use what is known as "key commitment", a process by which an encrypted message can only be decrypted by one key; the key used to originally encrypt the message. 

In older versions of S3EC, when customers are also using a feature called "Instruction File" to store EDKs, key commitment is not implemented because multiple EDKs could be associated to an underlying encrypted message object.  For such customers an attack that leverages the lack of key commitment is possible. A bad actor would need two things to leverage this issue: (i) the ability to create a separate, rogue, EDK that will also decrypt the underlying object to produce desired plaintext, and (ii) permission to upload a new instruction file to the S3 bucket to replace the existing instruction file placed there by the user using the S3C. Any future attempt to decrypt the underlying encrypted message with the S3EC will unwittingly use the rogue EDK to produce a valid plaintext message.

Impacted versions: <= 3.367.0



## Patches

We are introducing the concept of "key commitment" to S3EC where the EDK is cryptographically bound to the ciphertext in order to address this issue.  In order to maintain compatibility for in-flight messages we are releasing the fix in two versions.  A code-compatible minor version that can read messages with key-commitment but not write them, and a new major version that can both read and write messages with key-commitment.  For maximum safety customers are asked to upgrade to the latest major version: 3.368.0 or later.



## Workarounds

There are no workarounds, please upgrade to the suggested version of S3EC.

## References

If customeres have any questions or comments about this advisory, AWS SDK for PHP asks that they contact AWS Security via the issue reporting page or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/aws-sdk-php/security/advisories/GHSA-x8cp-jf6f-r4xh
- https://nvd.nist.gov/vuln/detail/CVE-2025-14761
- https://github.com/aws/aws-sdk-php/commit/6827cac70397dca07e6e86f7cf630954ec2bc6bf
- https://aws.amazon.com/security/security-bulletins/AWS-2025-032
- https://github.com/FriendsOfPHP/security-advisories/blob/master/aws/aws-sdk-php/CVE-2025-14761.yaml
- https://github.com/aws/aws-sdk-php
- https://github.com/aws/aws-sdk-php/releases/tag/3.368.0
