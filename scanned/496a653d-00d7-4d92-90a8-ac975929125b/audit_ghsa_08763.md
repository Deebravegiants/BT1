# [H] awslabs/tough Delegated Roles have a Signature Threshold Bypass

## Summary
Severity: High
Advisory: GHSA-8m7c-8m39-rv4x
CVE: CVE-2026-6966
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-8m7c-8m39-rv4x
Type: github-advisory

## Affected
- crates.io: `tough` — affected >=0 <0.22.0
- crates.io: `tuftool` — affected >=0 <0.15.0

## Details
### Summary
Improper verification of cryptographic signature uniqueness in delegated role validation in awslabs/tough before tough-v0.22.0 allows remote authenticated users to bypass the TUF signature threshold requirement by duplicating a valid signature, causing the client to accept forged delegated role metadata.

### Impact
The tough library, prior to 0.22.0, does not properly verify the uniqueness of keys in the signatures provided to meet the threshold of cryptographic signatures in delegated targets. It allows actors with access to a valid signing key to create multiple valid signatures in order to circumvent TUF requiring a minimum threshold of unique keys before the metadata is considered valid.

### Patches
This issue has been addressed in tough version 0.22.0 and tuftool version 0.15.0. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes. 

### Workarounds
No workarounds to this issue are known.

### References
* CVE-2026-6966

If there are any questions or comments about this advisory, please contact [AWS/Amazon] Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Acknowledgement

Amazon Web Services Labs would like to thank Emily Albini of Oxide Computer and Oleh Konko of 1seal for collaborating on this issue through the coordinated vulnerability disclosure process

## References
- https://github.com/awslabs/tough/security/advisories/GHSA-8m7c-8m39-rv4x
- https://nvd.nist.gov/vuln/detail/CVE-2026-6966
- https://aws.amazon.com/security/security-bulletins/2026-019-aws
- https://crates.io/crates/tough/0.22.0
- https://crates.io/crates/tuftool/0.15.0
- https://github.com/awslabs/tough
- https://github.com/awslabs/tough/releases/tag/tough-v0.22.0
- https://github.com/awslabs/tough/releases/tag/tuftool-v0.15.0
