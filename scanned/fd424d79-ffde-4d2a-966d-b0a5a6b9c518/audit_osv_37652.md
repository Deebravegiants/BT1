# [M] Homarr has a Race Condition in Invite Token Registration (TOCTOU)

## Summary
Severity: Medium
Advisory: CVE-2026-32602
Aliases: GHSA-vfw3-53q9-2hp8
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-32602
Type: osv

## Details
Homarr is an open-source dashboard. Prior to 1.57.0, the user registration endpoint (/api/trpc/user.register) is vulnerable to a race condition that allows an attacker to create multiple user accounts from a single-use invite token. The registration flow performs three sequential database operations without a transaction: CHECK, CREATE, and DELETE. Because these operations are not atomic, concurrent requests can all pass the validation step (1) before any of them reaches the deletion step (3). This allows multiple accounts to be registered using a single invite token that was intended to be single-use. This vulnerability is fixed in 1.57.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32602.json
- https://github.com/homarr-labs/homarr/security/advisories/GHSA-vfw3-53q9-2hp8
- https://nvd.nist.gov/vuln/detail/CVE-2026-32602
