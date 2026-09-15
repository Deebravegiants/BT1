# [H] NervesHub has Insufficient Token Entropy that Allows Authentication Bypass via Brute Force

## Summary
Severity: High
Advisory: CVE-2025-64097
Aliases: GHSA-m9vj-776q-vc8m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:H)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2025-64097
Type: osv

## Details
NervesHub is a web service that allows users to manage over-the-air (OTA) firmware updates of devices in the field. A vulnerability present starting in version 1.0.0 and prior to version 2.3.0 allowed attackers to brute-force user API tokens due to the predictable format of previously issued tokens. Tokens included user-identifiable components and were not cryptographically secure, making them susceptible to guessing or enumeration. The vulnerability could have allowed unauthorized access to user accounts or API actions protected by these tokens. A fix is available in version 2.3.0 of NervesHub. This version introduces strong, cryptographically-random tokens using `:crypto.strong_rand_bytes/1`, hashing of tokens before database storage to prevent misuse even if the database is compromised, and context-aware token storage to distinguish between session and API tokens. There are no practical workarounds for this issue other than upgrading. In sensitive environments, as a temporary mitigation,
firewalling access to the NervesHub server can help limit exposure until an upgrade is possible.

## References
- https://github.com/nerves-hub/nerves_hub_web/releases/tag/v2.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64097.json
- https://github.com/nerves-hub/nerves_hub_web/security/advisories/GHSA-m9vj-776q-vc8m
- https://nvd.nist.gov/vuln/detail/CVE-2025-64097
- https://github.com/nerves-hub/nerves_hub_web/pull/2024
