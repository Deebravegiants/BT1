# [H] RustFS: ImportIam Allows Creation of Backdoor Service Accounts Under Any Parent Including Root

## Summary
Severity: High
Advisory: CVE-2026-45043
Aliases: GHSA-566f-q62r-wcr8
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45043
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. Prior to 1.0.0-beta.2, improper validation in the PUT /rustfs/admin/v3/import-iam endpoint allows a user with ImportIAMAction to create service accounts under arbitrary parent identities, including the root user (minioadmin). The endpoint accepts attacker-controlled parent, claims, accessKey, and secretKey values without enforcing privilege boundaries or sanitization. This enables privilege escalation to full administrative access using a persistent, attacker-defined credential. This vulnerability is fixed in 1.0.0-beta.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45043.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-566f-q62r-wcr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-45043
