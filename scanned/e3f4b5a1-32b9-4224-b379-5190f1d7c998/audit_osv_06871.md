# [M] MongoDB Server binaries may load potentially insecure shared libraries from specific relative paths

## Summary
Severity: Medium
Advisory: BIT-mongodb-2024-8207
Aliases: CVE-2024-8207
Ecosystem: Bitnami
Published: 2024-08-31
Source: https://osv.dev/vulnerability/BIT-mongodb-2024-8207
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=6.1.0 <7.0.7

## Details
In certain highly specific configurations of the host system and MongoDB server binary installation on Linux Operating Systems, it may be possible for a unintended actor with host-level access to cause the MongoDB Server binary to load unintended actor-controlled shared libraries when the server binary is started, potentially resulting in the unintended actor gaining full control over the MongoDB server process. This issue affects MongoDB Server v5.0 versions prior to 5.0.14 and MongoDB Server v6.0 versions prior to 6.0.3.

Required Configuration: Only environments with Linux as the underlying operating system is affected by this issue

## References
- https://jira.mongodb.org/browse/SERVER-69507
- https://nvd.nist.gov/vuln/detail/CVE-2024-8207
- https://security.netapp.com/advisory/ntap-20250516-0009/
