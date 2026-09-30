# [H] Pre-Authentication Denial of Service Vulnerability in MongoDB Server's OIDC Authentication

## Summary
Severity: High
Advisory: BIT-mongodb-2025-6709
Aliases: CVE-2025-6709
Ecosystem: Bitnami
Published: 2025-09-16
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-6709
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.5

## Details
The MongoDB Server is susceptible to a denial of service vulnerability due to improper handling of specific date values in JSON input when using OIDC authentication. This can be reproduced using the mongo shell to send a malicious JSON payload leading to an invariant failure and server crash. This issue affects MongoDB Server v7.0 versions prior to 7.0.17 and MongoDB Server v8.0 versions prior to 8.0.5.

The same issue affects MongoDB Server v6.0 versions prior to 6.0.21, but an attacker can only induce denial of service after authenticating.

## References
- https://jira.mongodb.org/browse/SERVER-106748
- https://nvd.nist.gov/vuln/detail/CVE-2025-6709
