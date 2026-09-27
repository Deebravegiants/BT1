# [M] Grav API Plugin before 1.0.10 Broken Access Control

## Summary
Severity: Medium
Advisory: CVE-2026-65895
Aliases: GHSA-4pqv-2qj5-38fp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65895
Type: osv

## Details
Grav API Plugin versions before 1.0.10 fail to restrict write access to security-critical plugin configuration scopes, allowing authenticated users with api.config.write privilege to modify rate limiting and CORS settings. Attackers can disable rate limiting site-wide to enable credential brute-forcing attacks and reconfigure CORS policies to include attacker-controlled origins with credentials enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65895.json
- https://github.com/getgrav/grav/security/advisories/GHSA-4pqv-2qj5-38fp
- https://nvd.nist.gov/vuln/detail/CVE-2026-65895
- https://www.vulncheck.com/advisories/grav-api-plugin-before-broken-access-control
- https://github.com/getgrav/grav-plugin-api/commit/f9438d4e71389b1041ac60b69b0b5714ecfa3bdd
