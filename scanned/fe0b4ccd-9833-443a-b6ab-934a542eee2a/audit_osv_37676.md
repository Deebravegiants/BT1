# [M] Coolify read-scoped API tokens can perform state-changing validation operations

## Summary
Severity: Medium
Advisory: CVE-2026-32718
Aliases: GHSA-f47p-xrgc-977v
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-32718
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.466, mutating API validation endpoints are guarded by read ability, allowing read-scoped API tokens to perform state-changing operations such as validating cloud tokens and servers. This issue is fixed in version 4.0.0-beta.466.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32718.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-f47p-xrgc-977v
- https://nvd.nist.gov/vuln/detail/CVE-2026-32718
- https://github.com/coollabsio/coolify/commit/c15bcd56347fc8c535755791e92e4f6c2af17e3a
- https://github.com/coollabsio/coolify/pull/8893
