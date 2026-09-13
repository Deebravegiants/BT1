# [M] Grav before 2.0.16 Information Disclosure via Twig Sandbox

## Summary
Severity: Medium
Advisory: CVE-2026-76846
Aliases: GHSA-xjw5-q542-3vmr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-76846
Type: osv

## Details
Grav before 2.0.16 contains an incomplete default denylist in the Twig sandbox configuration that fails to block access to system configuration secrets. Attackers with page-edit permission can use config.get() or config.toArray() in Twig templates to retrieve sensitive values like system.cache.redis.password when config_access is enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76846.json
- https://github.com/getgrav/grav/security/advisories/GHSA-xjw5-q542-3vmr
- https://nvd.nist.gov/vuln/detail/CVE-2026-76846
- https://www.vulncheck.com/advisories/grav-before-information-disclosure-via-twig-sandbox
