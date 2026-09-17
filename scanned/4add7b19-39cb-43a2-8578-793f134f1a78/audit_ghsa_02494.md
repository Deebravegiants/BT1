# [H] Improper verification of signature threshold in tough

## Summary
Severity: High
Advisory: GHSA-5q2r-92f9-4m49
CVE: CVE-2020-15093
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-5q2r-92f9-4m49
Type: github-advisory

## Affected
- crates.io: `tough` — affected >=0 <0.7.1

## Details
## Impact

The tough library, prior to 0.7.1, does not properly verify the uniqueness of keys in the signatures provided to meet the threshold of cryptographic signatures. It allows someone with access to a valid signing key to create multiple valid signatures in order to circumvent TUF requiring a minimum threshold of unique keys before the metadata is considered valid.

AWS would like to thank Erick Tryzelaar of the Google Fuchsia Team for reporting this issue. 

## Patches

A fix is available in version 0.7.1.

## Workarounds

No workarounds to this issue are known.

## References

CVE-2020-6174 is assigned to the same issue in the TUF reference implementation.

https://github.com/theupdateframework/tuf/pull/974
https://nvd.nist.gov/vuln/detail/CVE-2020-6174

## For more information

If you have any questions or comments about this advisory, [contact AWS Security](https://aws.amazon.com/security/vulnerability-reporting/) at [aws-security@amazon.com](mailto:aws-security@amazon.com).

## References
- https://github.com/awslabs/tough/security/advisories/GHSA-5q2r-92f9-4m49
- https://nvd.nist.gov/vuln/detail/CVE-2020-15093
- https://github.com/theupdateframework/tuf/pull/974
- https://github.com/theupdateframework/tuf/commit/2977188139d065ff3356c3cb4aec60c582b57e0e
- https://github.com/awslabs/tough
- https://rustsec.org/advisories/RUSTSEC-2020-0024.html
