# [M] CVE-2025-14764

## Summary
Severity: Medium
Advisory: CVE-2025-14764
Aliases: GHSA-3g75-q268-r9r6, GO-2025-4250
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-14764
Type: osv

## Details
Missing cryptographic key commitment in the Amazon S3 Encryption Client for Go may allow a user with write access to the S3 bucket to introduce a new EDK that decrypts to different plaintext when the encrypted data key is stored in an "instruction file" instead of S3's metadata record.


To mitigate this issue, upgrade Amazon S3 Encryption Client for Go to version 4.0 or later.

## References
- https://aws.amazon.com/security/security-bulletins/AWS-2025-032/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14764.json
- https://github.com/aws/amazon-s3-encryption-client-go/security/advisories/GHSA-3g75-q268-r9r6
- https://nvd.nist.gov/vuln/detail/CVE-2025-14764
- https://github.com/aws/amazon-s3-encryption-client-go/releases/tag/v4.0.0
