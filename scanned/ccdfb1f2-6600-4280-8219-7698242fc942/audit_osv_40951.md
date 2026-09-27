# [M] Capgo - Information Disclosure via get_orgs_v7 RPC Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-56279
Aliases: GHSA-fch8-pp28-mw2x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-56279
Type: osv

## Details
Capgo before 12.128.2 contains an information disclosure vulnerability in the get_orgs_v7(userid) RPC function that remains publicly invokable despite intended private access controls. Unauthenticated attackers can supply arbitrary user UUIDs to retrieve foreign users' organization membership, roles, management emails, and billing metadata.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56279.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-fch8-pp28-mw2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-56279
- https://www.vulncheck.com/advisories/capgo-information-disclosure-via-get-orgs-v7-rpc-endpoint
