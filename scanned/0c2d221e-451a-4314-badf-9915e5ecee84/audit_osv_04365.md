# [H] Possible Server-Side Request Forgery (SSRF) in webhooks

## Summary
Severity: High
Advisory: BIT-discourse-2022-39241
Aliases: CVE-2022-39241, GHSA-rcc5-28r3-23rr
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-39241
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.10

## Details
Discourse is a platform for community discussion. A malicious admin could use this vulnerability to perform port enumeration on the local host or other hosts on the internal network, as well as against hosts on the Internet. Latest `stable`, `beta`, and `test-passed` versions are now patched. As a workaround, self-hosters can use `DISCOURSE_BLOCKED_IP_BLOCKS` env var (which overrides `blocked_ip_blocks` setting) to stop webhooks from accessing private IPs.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-rcc5-28r3-23rr
- https://nvd.nist.gov/vuln/detail/CVE-2022-39241
