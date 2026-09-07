# [H] CRL Distribution Point Scope Check Logic Error in AWS-LC

## Summary
Severity: High
Advisory: GHSA-9f94-5g5w-gf6r
CWE: CWE-295
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-9f94-5g5w-gf6r
Type: github-advisory

## Affected
- crates.io: `aws-lc-fips-sys` — affected >=0.13.0 <0.13.13
- crates.io: `aws-lc-sys` — affected >=0.15.0 <0.39.0

## Details
### Summary

AWS-LC is an open-source, general-purpose cryptographic library.

### Impact 

A logic error in CRL distribution point matching in AWS-LC allows a revoked certificate to bypass revocation checks during certificate validation, when the application enables CRL checking and uses partitioned CRLs with Issuing Distribution Point (IDP) extensions.

Customers of AWS services do not need to take action. aws-lc-sys and aws-lc-fips-sys contain code from AWS-LC. Applications using aws-lc-sys or aws-lc-fips-sys should upgrade to the most recent releases of aws-lc-sys or aws-lc-fips-sys.

### Impacted versions:
* aws-lc-sys >= v0.15.0, < v0.39.0
* aws-lc-fips-sys >= v0.13.0, < v0.13.13

### Patches 

The patch is included in aws-lc-sys v0.39.0 and aws-lc-fips-sys v0.13.13.

### Workarounds

Applications can workaround this issue if they do not enable CRL checking (X509_V_FLAG_CRL_CHECK). Applications using complete (non-partitioned) CRLs without IDP extensions are also not affected.

Otherwise, there is no workaround and applications using aws-lc-sys or aws-lc-fips-sys should upgrade to the most recent releases of aws-lc-sys or aws-lc-fips-sys.

### References

If you have any questions or comments about this advisory, we ask that you contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting/) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/aws-lc-rs/security/advisories/GHSA-9f94-5g5w-gf6r
- https://aws.amazon.com/security/security-bulletins/2026-010-AWS
- https://github.com/aws/aws-lc-rs
- https://rustsec.org/advisories/RUSTSEC-2026-0042.html
- https://rustsec.org/advisories/RUSTSEC-2026-0048.html
