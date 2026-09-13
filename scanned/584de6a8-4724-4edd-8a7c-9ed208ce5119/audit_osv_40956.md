# [M] Capgo - Unauthenticated API Key Validity and Permission Oracle via RPC Functions

## Summary
Severity: Medium
Advisory: CVE-2026-56300
Aliases: GHSA-7r6g-whg3-5mm4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-56300
Type: osv

## Details
Capgo before 12.128.2 contains unauthenticated security definer RPC functions get_user_id and get_org_perm_for_apikey that expose API key validity oracles and user UUID disclosure. Unauthenticated attackers using the public API key can validate leaked keys, enumerate users and apps, and determine permission levels, significantly increasing the actionability of compromised credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56300.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-7r6g-whg3-5mm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-56300
- https://www.vulncheck.com/advisories/capgo-unauthenticated-api-key-validity-and-permission-oracle-via-rpc-functions
