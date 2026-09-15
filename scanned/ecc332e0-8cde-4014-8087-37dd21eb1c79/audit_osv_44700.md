# [C] Traefik before v2.11.55 and v3.0.0 through v3.7.10 Authentication Bypass via digestAuth

## Summary
Severity: Critical
Advisory: CVE-2026-85595
Aliases: GHSA-5w68-77r2-r64c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85595
Type: osv

## Details
Traefik versions before v2.11.55 and versions v3.0.0 through v3.7.10 contain an authentication bypass vulnerability in the digestAuth middleware where unknown usernames receive an empty secret instead of rejection. Attackers can compute a valid digest response using the empty secret and arbitrary credentials to bypass authentication on any digestAuth-protected route without a valid username or password.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85595.json
- https://github.com/traefik/traefik/security/advisories/GHSA-5w68-77r2-r64c
- https://nvd.nist.gov/vuln/detail/CVE-2026-85595
- https://www.vulncheck.com/advisories/traefik-before-2.11.55-authentication-bypass-via-digestauth
