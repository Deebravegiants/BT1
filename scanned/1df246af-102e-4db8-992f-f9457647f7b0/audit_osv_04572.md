# [M] Discourse: Onebox Domain Blocklist Bypass via Case-Sensitive Comparison

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-72721
Aliases: CVE-2026-72721, GHSA-3x7x-24rq-h5j6
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-discourse-2026-72721
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.6.0 <2026.6.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0, Onebox::DomainChecker.is_blocked? compares hostnames and SiteSetting.blocked_onebox_domains entries case-sensitively, allowing an attacker to bypass configured Onebox domain restrictions by changing character casing in a redirect target hostname. This issue is fixed in versions 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0.

## References
- https://github.com/discourse/discourse/commit/a3e10759fef47f03d450649bb51d9e84f4c68b8f
- https://github.com/discourse/discourse/commit/c2eb6b0e5597d6f28f4be739b83300bc9c69e3cd
- https://github.com/discourse/discourse/commit/caa615c371b1696982ee11ac8f3558f0f8ced584
- https://github.com/discourse/discourse/commit/f503971d311b7b0dfdb751ee8cfd67e8cb99f5c5
- https://github.com/discourse/discourse/pull/42091
- https://github.com/discourse/discourse/pull/42092
- https://github.com/discourse/discourse/pull/42093
- https://github.com/discourse/discourse/pull/42094
- https://github.com/discourse/discourse/security/advisories/GHSA-3x7x-24rq-h5j6
- https://nvd.nist.gov/vuln/detail/CVE-2026-72721
