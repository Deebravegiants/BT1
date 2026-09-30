# [M] AWS SDK for Rust will log AWS credentials when TRACE-level logging is enabled for request sending

## Summary
Severity: Medium
Advisory: GHSA-mjv9-vp6w-3rc9
CVE: CVE-2023-30610
CWE: CWE-532
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-mjv9-vp6w-3rc9
Type: github-advisory

## Affected
- crates.io: `aws-sigv4` — affected >=0.55.0 <0.55.1
- crates.io: `aws-sigv4` — affected >=0.54.1 <0.54.2
- crates.io: `aws-sigv4` — affected >=0.53.1 <0.53.2
- crates.io: `aws-sigv4` — affected >=0.52.0 <0.52.1
- crates.io: `aws-sigv4` — affected >=0.51.0 <0.51.1
- crates.io: `aws-sigv4` — affected >=0.49.0 <0.49.1
- crates.io: `aws-sigv4` — affected >=0.48.0 <0.48.1
- crates.io: `aws-sigv4` — affected >=0.47.0 <0.47.1
- crates.io: `aws-sigv4` — affected >=0.46.0 <0.46.1
- crates.io: `aws-sigv4` — affected >=0.15.0 <0.15.1
- crates.io: `aws-sigv4` — affected >=0.14.0 <0.14.1
- crates.io: `aws-sigv4` — affected >=0.13.0 <0.13.1
- crates.io: `aws-sigv4` — affected >=0.12.0 <0.12.1
- crates.io: `aws-sigv4` — affected >=0.11.0 <0.11.1
- crates.io: `aws-sigv4` — affected >=0.10.1 <0.10.2
- crates.io: `aws-sigv4` — affected >=0.9.0 <0.9.1
- crates.io: `aws-sigv4` — affected >=0.8.0 <0.8.1
- crates.io: `aws-sigv4` — affected >=0.7.0 <0.7.1
- crates.io: `aws-sigv4` — affected >=0.6.0 <0.6.1
- crates.io: `aws-sigv4` — affected >=0.5.2 <0.5.3
- crates.io: `aws-sigv4` — affected >=0.4.1 <0.4.2
- crates.io: `aws-sigv4` — affected >=0.3.0 <0.3.1
- crates.io: `aws-sigv4` — affected >=0.2.0 <0.2.1

## Details
The `aws_sigv4::SigningParams` struct had a derived `Debug` implementation. When debug-formatted, it would include a user's AWS access key, AWS secret key, and security token in plaintext. When TRACE-level logging is enabled for an SDK, `SigningParams` is printed, thereby revealing those credentials to anyone with access to logs.

### Impact
All users of the AWS SDK for Rust who enabled TRACE-level logging, either globally (e.g. `RUST_LOG=trace`), or for the `aws-sigv4` crate specifically.

### Patches
- Versions >= `0.55.1`
- `0.54.2`
- `0.53.2`
- `0.52.1`
- `0.51.1`
- `0.50.1`
- `0.49.1`
- `0.48.1`
- `0.47.1`
- `0.46.1`
- `0.15.1`
- `0.14.1`
- `0.13.1`
- `0.12.1`
- `0.11.1`
- `0.10.2`
- `0.9.1`
- `0.8.1`
- `0.7.1`
- `0.6.1`
- `0.5.3`
- `0.3.1`
- `0.2.1`

### Workarounds
Disable TRACE-level logging for AWS Rust SDK crates.

## References
- https://github.com/awslabs/aws-sdk-rust/security/advisories/GHSA-mjv9-vp6w-3rc9
- https://nvd.nist.gov/vuln/detail/CVE-2023-30610
- https://github.com/awslabs/aws-sdk-rust
- https://rustsec.org/advisories/RUSTSEC-2023-0125.html
