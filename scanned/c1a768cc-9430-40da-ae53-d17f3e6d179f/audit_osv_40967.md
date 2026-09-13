# [M] Capgo - Channel Configuration Mutation via Write-Scoped API Keys

## Summary
Severity: Medium
Advisory: CVE-2026-56335
Aliases: GHSA-ph9c-vwjq-pqhj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-56335
Type: osv

## Details
Capgo before 12.128.2 contains an authorization bypass vulnerability where write-scoped API keys can directly mutate protected channel configuration fields through PostgREST by exploiting a null authentication check in the immutability trigger. Attackers with write API keys can modify sensitive channel attributes such as public, allow_emulator, and security-related flags outside intended application routes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56335.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-ph9c-vwjq-pqhj
- https://nvd.nist.gov/vuln/detail/CVE-2026-56335
- https://www.vulncheck.com/advisories/capgo-channel-configuration-mutation-via-write-scoped-api-keys
