# [H] AWS-LC has Timing Side-Channel in AES-CCM Tag Verification

## Summary
Severity: High
Advisory: GHSA-65p9-r9h6-22vj
CWE: CWE-208
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-65p9-r9h6-22vj
Type: github-advisory

## Affected
- crates.io: `aws-lc-sys` — affected >=0.14.0 <0.38.0
- crates.io: `aws-lc-fips-sys` — affected >=0.13.0 <0.13.12

## Details
### Summary
AWS-LC is an open-source, general-purpose cryptographic library.

### Impact
Observable timing discrepancy in AES-CCM decryption in AWS-LC allows an unauthenticated user to potentially determine authentication tag validity via timing analysis.

The impacted implementations are through the EVP CIPHER API: EVP_aes_128_ccm, EVP_aes_192_ccm, and EVP_aes_256_ccm.

Customers of AWS services do not need to take action. aws-lc-sys and aws-lc-fips-sys contain code from AWS-LC. Applications using aws-lc-sys or aws-lc-fips-sys should upgrade to the most recent releases of aws-lc-sys or aws-lc-fips-sys.

### Impacted versions: 
 - aws-lc-sys versions: >= 0.14.0, < 0.38.0
 - aws-lc-fips-sys versions: >= v0.13.0, < 0.13.12.

### Patches
The patch is included in aws-lc-sys v.0.38.0 and aws-lc-fips-sys v0.13.12.

### Workarounds
In the special cases of using AES-CCM with (M=4, L=2), (M=8, L=2), or (M=16, L=2), applications can workaround this issue by using AES-CCM through the EVP AEAD API using implementations EVP_aead_aes_128_ccm_bluetooth, EVP_aead_aes_128_ccm_bluetooth_8, and, EVP_aead_aes_128_ccm_matter respectively.

Otherwise, there is no workaround and applications using aws-lc-sys or aws-lc-fips-sys should upgrade to the most recent releases of aws-lc-sys or aws-lc-fips-sys.

### Resources
If there are any questions or comments about this advisory, contact [AWS/Amazon] Security via the[vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Acknowledgement
AWS-LC would like to thank Joshua Rogers (https://joshua.hu/) for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/aws/aws-lc-rs/security/advisories/GHSA-65p9-r9h6-22vj
- https://github.com/aws/aws-lc/security/advisories/GHSA-frmv-5gcm-jwxh
- https://nvd.nist.gov/vuln/detail/CVE-2026-3337
- https://aws.amazon.com/security/security-bulletins/2026-005-AWS
- https://github.com/aws/aws-lc-rs
- https://rustsec.org/advisories/RUSTSEC-2026-0043.html
- https://rustsec.org/advisories/RUSTSEC-2026-0045.html
