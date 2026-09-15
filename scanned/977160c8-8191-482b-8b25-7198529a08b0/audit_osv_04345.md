# [M] Denial of Service in discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2021-43850
Aliases: CVE-2021-43850, GHSA-59jr-pj65-qmvr
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2021-43850
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.7.12

## Details
Discourse is an open source platform for community discussion. In affected versions admins users can trigger a Denial of Service attack via the `/message-bus/_diagnostics` path. The impact of this vulnerability is greater on multisite Discourse instances (where multiple forums are served from a single application server) where any admin user on any of the forums are able to visit the `/message-bus/_diagnostics` path. The problem has been patched. Please upgrade to 2.8.0.beta10 or 2.7.12. No workarounds for this issue exist.

## References
- https://github.com/discourse/discourse/commit/7a8ec129fb54f188b2da6588c9d24d3a36eb0d39
- https://github.com/discourse/discourse/security/advisories/GHSA-59jr-pj65-qmvr
- https://nvd.nist.gov/vuln/detail/CVE-2021-43850
