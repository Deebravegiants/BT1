# [M] MinIO allows an SFTP authentication bypass due to improperly trusted SSH key

## Summary
Severity: Medium
Advisory: GHSA-wc79-7x8x-2p58
CVE: CVE-2025-27414
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-03
Source: https://github.com/advisories/GHSA-wc79-7x8x-2p58
Type: github-advisory

## Affected
- Go: `github.com/minio/minio` — affected >=0.0.0-20240605075113-91e1487de457 <0.0.0-20250227184332-4c71f1b4ec0f

## Details
### Summary
_A bug in evaluating the trust of the SSH key used in an SFTP connection to MinIO allows authentication bypass and unauthorized data access._

### Details

On a MinIO server with SFTP access configured and using LDAP as an external identity provider, MinIO supports SSH key based authentication for SFTP connections when the user has the `sshPublicKey` attribute set in their LDAP server. The server trusts the client's key only when the public key is the same as the `sshPublicKey` attribute.

Due to the bug, when the user has no `sshPublicKey` property in LDAP, the server ends up trusting the key allowing the client to perform any FTP operations allowed by the MinIO access policies associated with the LDAP user (or any of their groups).

The bug was introduced in https://github.com/minio/minio/commit/91e1487de45720753c9e9e4c02b1bd16b7e452fa.

### Impact

The following requirements must be met to exploit this vulnerability:

1. MinIO server must be configured to allow SFTP access and use LDAP as an external identity provider.
2. Knowledge of an LDAP username that does not have the `sshPublicKey` property set.
3. Such an LDAP username or one of their groups must also have some MinIO access policy configured.

When this bug is successfully exploited, the attacker can perform any FTP operations (i.e. reading, writing, deleting and listing objects) allowed by the access policy associated with the LDAP user account (and their groups).

## References
- https://github.com/minio/minio/security/advisories/GHSA-wc79-7x8x-2p58
- https://nvd.nist.gov/vuln/detail/CVE-2025-27414
- https://github.com/minio/minio/commit/4c71f1b4ec0fb2a473ddaac18c20ec9e63f267ec
- https://github.com/minio/minio/commit/91e1487de45720753c9e9e4c02b1bd16b7e452fa
- https://github.com/minio/minio
