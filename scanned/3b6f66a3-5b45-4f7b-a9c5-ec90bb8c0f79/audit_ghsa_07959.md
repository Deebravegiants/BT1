# [H] Antrea has invalid enforcement order for network policy rules caused by integer overflow

## Summary
Severity: High
Advisory: GHSA-86x4-wp9f-wrr9
CVE: CVE-2026-25804
CWE: CWE-287, CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-86x4-wp9f-wrr9
Type: github-advisory

## Affected
- Go: `antrea.io/antrea` — affected >=0 <2.3.2
- Go: `antrea.io/antrea` — affected >=2.4.0 <2.4.3

## Details
### Impact

Antrea's network policy priority assignment system has a uint16 arithmetic overflow bug that causes incorrect OpenFlow priority calculations when handling a large numbers of policies with various priority values. This results in potentially incorrect traffic enforcement.

If a user creates a large number of Antrea NetworkPolicies (ANP or ACNP) with varying priorities, some rules with lower logical priorities (higher numerical priority values) may take precedence over rules with higher logical priorities (lower numerical priority values). Traffic that should be denied by the configured Antrea NetworkPolicies may end up being allowed, potentially letting an attacker access a sensitive service. Traffic that should be allowed by the configured Antrea NetworkPolicies may end up being denied, breaking applications and potentially opening the door for denial-of-service attacks.

The Antrea NetworkPolicy system comes with support for priority Tiers. Rules defined within a Tier cannot take precedence over rules defined in higher priority Tiers. Some users / roles may only be authorized to define within specific Tiers. This security vulnerability enables such users to intentionally "escape" their Tier and override rules in higher priority Tiers.

Antrea deployments that *only* use upstream Kubernetes NetworkPolicies - and do not use Antrea NetworkPolicies - are not affected.

### Patches
https://github.com/antrea-io/antrea/pull/7496
Antrea v2.5.0
Antrea v2.4.3
Antrea v2.3.2

### Workarounds

Antrea deployments that *only* use upstream Kubernetes NetworkPolicies - and do not use Antrea NetworkPolicies - are not affected.

For users leveraging Antrea NetworkPolicies, there is no way to fix or remediate the vulnerability without upgrading.

### Resources

https://gist.github.com/antoninbas/c429cc3e5bb8479ba7ff38fd6fde59d9
https://github.com/antrea-io/antrea/pull/7496
https://github.com/antrea-io/antrea/blob/main/docs/antrea-network-policy.md

## References
- https://github.com/antrea-io/antrea/security/advisories/GHSA-86x4-wp9f-wrr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-25804
- https://github.com/antrea-io/antrea/pull/7496
- https://github.com/antrea-io/antrea/commit/86c4b6010f3be536866f339b632621c23d7186fa
- https://gist.github.com/antoninbas/c429cc3e5bb8479ba7ff38fd6fde59d9
- https://github.com/antrea-io/antrea
- https://github.com/antrea-io/antrea/blob/main/docs/antrea-network-policy.md
