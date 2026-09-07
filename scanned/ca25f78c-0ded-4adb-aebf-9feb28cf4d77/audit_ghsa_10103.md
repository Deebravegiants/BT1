# [M] AWS Encryption SDK for Python: Key commitment policy bypass via shared key cache

## Summary
Severity: Medium
Advisory: GHSA-v638-38fc-rhfv
CVE: CVE-2026-6550
CWE: CWE-757
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-v638-38fc-rhfv
Type: github-advisory

## Affected
- PyPI: `aws-encryption-sdk` — affected >=2.0.0 <3.3.1
- PyPI: `aws-encryption-sdk` — affected >=4.0.0 <4.0.5

## Details
## Summary
AWS Encryption SDK (ESDK) for Python is a client-side encryption library. An issue exists where, under certain circumstances, a specific cryptographic algorithm downgrade in the caching layer might allow an authenticated local threat actor to bypass key commitment policy enforcement via a shared key cache, resulting in ciphertext that can be decrypted to multiple different plaintexts.

## Impact
This issue requires all of the following conditions to be true: (1) Two ESDK for Python clients with different commitment policies share a single CachingCryptoMaterialsManager instance within the same process. (2) The client with the weaker commitment policy encrypts first, warming the cache. (3) Both clients use matching encryption contexts. (4) Both clients use the pre-configured default algorithm suite.

These conditions may occur during a migration from ESDK for Python v1 to newer versions, as v1 did not support key commitment.

When the weaker-policy client encrypts first, the cache stores encryption materials that do not enforce key commitment. Subsequent callers — including those configured to require key commitment — are served these cached materials instead of generating new ones that satisfy their policy. This results in encryption without key commitment, meaning the same ciphertext can be validly decrypted to different plaintexts under different keys (the "Invisible Salamanders" issue; see https://github.com/google/security-research/security/advisories/GHSA-wqgp-vphw-hphf). A threat actor who controls ciphertext can cause a recipient to decrypt a message different from what the sender encrypted, breaking message integrity.

## Impacted versions
- From 2.0 to 2.5.1
- From 3.0 to 3.3.0
- From 4.0 to 4.0.4

## Patches
This issue has been addressed in ESDK for Python versions 3.3.1 and 4.0.5. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

## Workarounds
If a customer requires operating multiple instances of the Python ESDK each with differently configured key commitment policies, they must not share a key cache.

References
If there are any questions or comments about this advisory, contact AWS Security through the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## Acknowledgement
Thanks to [1seal.org](http://1seal.org/) for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/aws/aws-encryption-sdk-python/security/advisories/GHSA-v638-38fc-rhfv
- https://github.com/google/security-research/security/advisories/GHSA-wqgp-vphw-hphf
- https://nvd.nist.gov/vuln/detail/CVE-2026-6550
- https://aws.amazon.com/security/security-bulletins/2026-017-aws
- https://github.com/aws/aws-encryption-sdk-python
- https://github.com/aws/aws-encryption-sdk-python/releases/tag/v3.3.1
- https://github.com/aws/aws-encryption-sdk-python/releases/tag/v4.0.5
