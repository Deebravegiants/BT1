# [M] Uncontrolled recursion in smithy-rs generated JSON, CBOR, and XML deserializers allows unauthenticated remote denial of service via recursive shapes

## Summary
Severity: Medium
Advisory: CVE-2026-15957
Aliases: GHSA-4f2p-7j38-4xrg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-15957
Type: osv

## Details
Smithy-RS is a Rust code generation and runtime framework that generates HTTP clients and servers from Smithy interface definitions, powering the AWS SDK for Rust and custom service implementations.



Uncontrolled recursion in the JSON, CBOR, and XML deserializer functions emitted by Amazon smithy-rs code generation could allow remote attackers to cause a denial of service (process abort via stack exhaustion) via a small request containing deeply nested data for a recursive model shape to a generated SDK or server.



To mitigate this issue, users should upgrade to aws-sdk-rust release-2026-06-02 or later. Users building custom servers with smithy-rs codegen should regenerate from smithy-rs release-2026-06-01 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-061-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15957.json
- https://github.com/smithy-lang/smithy-rs/security/advisories/GHSA-4f2p-7j38-4xrg
- https://nvd.nist.gov/vuln/detail/CVE-2026-15957
- https://github.com/awslabs/aws-sdk-rust/releases/tag/release-2026-06-02
