# [M] Cross-database write redirection via unvalidated dotted database name in bulk write namespaces

## Summary
Severity: Medium
Advisory: CVE-2026-81526
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81526
Type: osv

## Details
The MongoDB Rust Driver does not neutralize special characters in a caller-supplied target identifier before embedding it in the request it sends to the server. An actor able to influence that identifier in an application using the driver may cause write operations to be applied to an unintended target within the same deployment using the application's own credentials. This may result in unauthorized modification of data belonging to another logical boundary enforced by the application.

## References
- https://github.com/mongodb/mongo-rust-driver/releases/tag/v3.8.2
- https://jira.mongodb.org/browse/RUST-2467
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81526.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81526
