# [M] Coolify: Timing Attack in GitLab Webhook Token Validation

## Summary
Severity: Medium
Advisory: CVE-2026-27882
Aliases: GHSA-x525-46rq-mr8c
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-27882
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.461, the GitLab webhook endpoint uses a non-constant-time string comparison operator (!==) to validate the webhook secret token. This implementation is vulnerable to timing attacks, which could allow an attacker to gradually discover the secret token by measuring response time differences. This vulnerability is fixed in 4.0.0-beta.461.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27882.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-x525-46rq-mr8c
- https://nvd.nist.gov/vuln/detail/CVE-2026-27882
