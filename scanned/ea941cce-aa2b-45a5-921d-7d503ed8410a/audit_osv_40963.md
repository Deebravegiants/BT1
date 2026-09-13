# [M] Capgo - Information Disclosure via Unauthenticated /updates defaultChannel Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-56322
Aliases: GHSA-pgmr-gw53-7f77
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56322
Type: osv

## Details
Capgo before 12.128.2 contains an information disclosure vulnerability in the unauthenticated /updates endpoint that resolves the defaultChannel parameter before enforcing privacy restrictions, allowing attackers to enumerate private channels and leak version/config state. Unauthenticated attackers can probe private channel names and distinguish valid channels from nonexistent ones based on response differences, revealing assigned bundle versions and platform-specific configuration details.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56322.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-pgmr-gw53-7f77
- https://nvd.nist.gov/vuln/detail/CVE-2026-56322
- https://www.vulncheck.com/advisories/capgo-information-disclosure-via-unauthenticated-updates-defaultchannel-parameter
