# [H] AWS-LC has PKCS7_verify Signature Validation Bypass

## Summary
Severity: High
Advisory: GHSA-hfpc-8r3f-gw53
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-hfpc-8r3f-gw53
Type: github-advisory

## Affected
- crates.io: `aws-lc-sys` — affected >=0.24.0 <0.38.0

## Details
### Summary
AWS-LC is an open-source, general-purpose cryptographic library.

### Impact
Improper signature validation in PKCS7_verify() in AWS-LC allows an unauthenticated user to bypass signature verification when processing PKCS7 objects with Authenticated Attributes.

Customers of AWS services do not need to take action. aws-lc-sys contains code from AWS-LC. Applications using aws-lc-sys should upgrade to the most recent release of aws-lc-sys.

#### Impacted versions: 
aws-lc-sys versions: >= 0.24.0, < 0.38.0

### Patches
The patch is included in v0.38.0

### Workarounds
There is no workaround. Applications using aws-lc-sys should upgrade to the most recent release of aws-lc-sys.

### Resources
If there are any questions or comments about this advisory, contact [AWS/Amazon] Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/aws-lc-rs/security/advisories/GHSA-hfpc-8r3f-gw53
- https://github.com/aws/aws-lc/security/advisories/GHSA-jchq-39cv-q4wj
- https://nvd.nist.gov/vuln/detail/CVE-2026-3338
- https://aws.amazon.com/security/security-bulletins/2026-005-AWS
- https://github.com/aws/aws-lc-rs
- https://rustsec.org/advisories/RUSTSEC-2026-0047.html
