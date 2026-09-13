# [M] CVE-2025-14763

## Summary
Severity: Medium
Advisory: CVE-2025-14763
Aliases: GHSA-x44p-gvrj-pj2r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-14763
Type: osv

## Details
Missing cryptographic key commitment in the Amazon S3 Encryption Client for Java may allow a user with write access to the S3 bucket to introduce a new EDK that decrypts to different plaintext when the encrypted data key is stored in an "instruction file" instead of S3's metadata record.


To mitigate this issue, upgrade Amazon S3 Encryption Client for Java to version 4.0.0 or later.

## References
- https://aws.amazon.com/security/security-bulletins/AWS-2025-032/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14763.json
- https://github.com/aws/amazon-s3-encryption-client-java/security/advisories/GHSA-x44p-gvrj-pj2r
- https://nvd.nist.gov/vuln/detail/CVE-2025-14763
- https://github.com/aws/amazon-s3-encryption-client-java/releases/tag/v4.0.0
