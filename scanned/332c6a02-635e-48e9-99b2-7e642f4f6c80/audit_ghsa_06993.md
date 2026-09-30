# [H] Smithy-RS: Allocation of resources without limits in the default aws-smithy-http-server serve() path allows unauthenticated Slowloris denial of service

## Summary
Severity: High
Advisory: GHSA-jvxp-qmx7-gjpx
CVE: CVE-2026-16756
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-jvxp-qmx7-gjpx
Type: github-advisory

## Affected
- crates.io: `aws-smithy-http-server` — affected >=0 <0.66.5

## Details
## Summary
Smithy-RS is a Rust code generation and runtime framework that generates HTTP clients and servers from Smithy interface definitions, powering the AWS SDK for Rust and custom service implementations. An issue exists where, under certain circumstances, allocation of resources without limits in the default aws-smithy-http-server serve() path allows unauthenticated Slowloris denial of service. 

## Impact
Missing connection and header-read timeouts and the absence of a concurrent-connection cap in the default serve() path of Amazon aws-smithy-http-server might allow remote attackers to cause a denial of service by opening many connections and sending partial requests that are never completed, exhausting server sockets and tasks.

Impacted versions: aws-smithy-http-server <= 0.66.4

## Patches
This issue has been addressed in aws-smithy-http-server version 0.66.5. AWS recommends upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

## Workarounds
There is no workaround besides updating to the patched version.

## Contact
If you have any questions or comments about this advisory, AWS asks that you contact AWS Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/smithy-lang/smithy-rs/security/advisories/GHSA-jvxp-qmx7-gjpx
- https://nvd.nist.gov/vuln/detail/CVE-2026-16756
- https://aws.amazon.com/security/security-bulletins/2026-064-aws
- https://crates.io/crates/aws-smithy-http-server/0.66.5
- https://github.com/smithy-lang/smithy-rs
