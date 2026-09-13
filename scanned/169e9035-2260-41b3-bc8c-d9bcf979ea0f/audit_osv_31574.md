# [M] CVE-2025-14760

## Summary
Severity: Medium
Advisory: CVE-2025-14760
Aliases: GHSA-792f-r46x-r7gm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-14760
Type: osv

## Details
Missing cryptographic key commitment in the AWS SDK for C++ may allow a user with write access to the S3 bucket to introduce a new EDK that decrypts to different plaintext when the encrypted data key is stored in an "instruction file" instead of S3's metadata record.

To mitigate this issue, upgrade AWS SDK for C++ to version 1.11.712 or later

## References
- https://aws.amazon.com/security/security-bulletins/AWS-2025-032/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14760.json
- https://github.com/aws/aws-sdk-cpp/security/advisories/GHSA-792f-r46x-r7gm
- https://nvd.nist.gov/vuln/detail/CVE-2025-14760
- https://github.com/aws/aws-sdk-cpp/releases/tag/1.11.712
