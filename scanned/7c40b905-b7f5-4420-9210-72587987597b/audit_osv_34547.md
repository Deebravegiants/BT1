# [H] Karapace is vulnerable to Authentication Bypass

## Summary
Severity: High
Advisory: CVE-2025-61673
Aliases: GHSA-vq25-vcrw-gj53
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2025-10-03
Source: https://osv.dev/vulnerability/CVE-2025-61673
Type: osv

## Details
Karapace is an open-source implementation of Kafka REST and Schema Registry. Versions 5.0.0 and 5.0.1 contain an authentication bypass vulnerability when configured to use OAuth 2.0 Bearer Token authentication. If a request is sent without an Authorization header, the token validation logic is skipped entirely, allowing an unauthenticated user to read and write to Schema Registry endpoints that should otherwise be protected. This effectively renders the OAuth authentication mechanism ineffective. This issue is fixed in version 5.0.2.

## References
- https://github.com/Aiven-Open/karapace/pull/1143/commits/c4038e9ce9fa504b433d59ac2944e337292922c7
- https://github.com/Aiven-Open/karapace/releases/tag/5.0.2
- https://github.com/Aiven-Open/karapace/security/advisories/GHSA-vq25-vcrw-gj53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61673.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61673
