# [H] Klaw has an improper authorisation check on /resetMemoryCache

## Summary
Severity: High
Advisory: CVE-2026-25999
Aliases: GHSA-rp26-qv9w-xr5q
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2026-25999
Type: osv

## Details
Klaw is a self-service Apache Kafka Topic Management/Governance tool/portal. Prior to 2.10.2, there is an improper access control vulnerability that allows unauthorized users to trigger a reset or deletion of metadata for any tenant. By sending a crafted request to the /resetMemoryCache endpoint, an attacker can clear cached configurations, environments, and cluster data. This vulnerability is fixed in 2.10.2.

## References
- https://github.com/Aiven-Open/klaw/releases/tag/v2.10.2
- https://github.com/Aiven-Open/klaw/security/advisories/GHSA-rp26-qv9w-xr5q
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25999.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25999
- https://github.com/Aiven-Open/klaw/commit/617ed96b1db111ed498d89132321bf39f486e3a1
