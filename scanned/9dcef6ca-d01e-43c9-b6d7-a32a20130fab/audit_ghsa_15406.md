# [H] NetBird uses a static initialization vector (IV)

## Summary
Severity: High
Advisory: GHSA-9v35-4xcr-w9ph
CVE: CVE-2024-41260
CWE: CWE-321
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-9v35-4xcr-w9ph
Type: github-advisory

## Affected
- Go: `github.com/netbirdio/netbird` — affected >=0.23.2 <0.29.2

## Details
A static initialization vector (IV) in the encrypt function of netbird management's service from v0.23.2 to v0.29.1 allows attackers to obtain sensitive information (email addresses) when in possession of the audit events database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41260
- https://github.com/netbirdio/netbird/issues/2246
- https://github.com/github/advisory-database/pull/5714
- https://github.com/netbirdio/netbird/pull/2569
- https://github.com/netbirdio/netbird/commit/cf6210a6f42355e88c422c624376f6fcdaea6729
- https://gist.github.com/nyxfqq/92232108ac153e95d538bb17fc5ad636
- https://github.com/advisories/GHSA-9v35-4xcr-w9ph
- https://github.com/netbirdio/netbird
