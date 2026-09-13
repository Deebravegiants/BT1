# [M] Apache Arrow Rust Object Store: AWS WebIdentityToken exposure in log files

## Summary
Severity: Medium
Advisory: GHSA-c2hf-vcmr-qjrf
CVE: CVE-2024-41178
CWE: CWE-532
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-23
Source: https://github.com/advisories/GHSA-c2hf-vcmr-qjrf
Type: github-advisory

## Affected
- crates.io: `object_store` — affected >=0.5.0 <0.10.2

## Details
Exposure of temporary credentials in logs in Apache Arrow Rust Object Store (`object_store` crate), version 0.10.1 and earlier on all platforms using AWS WebIdentityTokens. 

On certain error conditions, the logs may contain the OIDC token passed to  AssumeRoleWithWebIdentity https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html . This allows someone with access to the logs to impersonate that identity, including performing their own calls to AssumeRoleWithWebIdentity, until the OIDC token expires. Typically OIDC tokens are valid for up to an hour, although this will vary depending on the issuer.

Users are recommended to use a different AWS authentication mechanism, disable logging or upgrade to version 0.10.2, which fixes this issue.

Details:

When using AWS WebIdentityTokens with the object_store crate, in the event of a failure and automatic retry, the underlying reqwest error, including the full URL with the credentials, potentially in the parameters, is written to the logs. 

Thanks to Paul Hatcherian for reporting this vulnerability

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41178
- https://github.com/apache/arrow-rs/pull/6074
- https://github.com/apache/arrow-rs/commit/4978e32654235f569062f2cad6c7361e410f1254
- https://github.com/apache/arrow-rs
- https://lists.apache.org/thread/3t0povdppnt2czv6crlsqhvyko93kcrg
- https://rustsec.org/advisories/RUSTSEC-2024-0358.html
- http://www.openwall.com/lists/oss-security/2024/07/23/3
