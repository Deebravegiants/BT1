# [H] AWS-LC X.509 Name Constraints Bypass via Wildcard/Unicode CN

## Summary
Severity: High
Advisory: GHSA-394x-vwmw-crm3
CWE: CWE-155, CWE-295
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-394x-vwmw-crm3
Type: github-advisory

## Affected
- crates.io: `aws-lc-sys` — affected >=0.32.0 <0.39.0

## Details
### Summary

AWS-LC is an open-source, general-purpose cryptographic library.

### Impact

A logic error in CN (Common Name) validation allows certificates with wildcard or raw UTF-8 Unicode CN values to bypass name constraints enforcement. The `cn2dnsid` function does not recognize these CN patterns as valid DNS identifiers, causing `NAME_CONSTRAINTS_check_CN` to skip validation. However, `X509_check_host` accepts these CN values when no dNSName SAN is present, allowing certificates to bypass name constraints while still being used for hostname verification.

Customers of AWS services do not need to take action. Applications using aws-lc-sys should upgrade to the most recent release of aws-lc-sys.

### Impacted versions:

* aws-lc-sys >= v0.32.0, < v0.39.0

### Patches

The patch is included in aws-lc-sys v0.39.0.

### Workarounds

Applications that set `X509_CHECK_FLAG_NEVER_CHECK_SUBJECT` to disable CN fallback are not affected. Applications that only encounter certificates with dNSName SANs (standard for public WebPKI) are also not affected.

Otherwise, there is no workaround and applications using aws-lc-sys should upgrade to the most recent releases of aws-lc-sys.

### References

If you have any questions or comments about this advisory, we ask that you contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting/) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Credits

Oleh Konko from 1seal (https://1seal.org/)

## References
- https://github.com/aws/aws-lc-rs/security/advisories/GHSA-394x-vwmw-crm3
- https://github.com/aws/aws-lc-rs
- https://rustsec.org/advisories/RUSTSEC-2026-0044.html
