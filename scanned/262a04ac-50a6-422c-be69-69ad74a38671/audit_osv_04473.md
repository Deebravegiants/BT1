# [M] Discourse has DoS vulnerability in username change endpoint

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-68659
Aliases: CVE-2025-68659, GHSA-rmp6-c9rq-6q7p
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2025-68659
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.0

## Details
Discourse is an open source discussion platform. Versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0 have an application level denial of service vulnerabilityin the username change functionality at try.discourse.org. The vulnerability allows attackers to cause noticeable server delays and resource exhaustion by sending large JSON payloads to the username preference endpoint PUT /u//preferences/username, resulting in degraded performance for other users and endpoints. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-rmp6-c9rq-6q7p
- https://nvd.nist.gov/vuln/detail/CVE-2025-68659
