# [M] Grav CMS before 2.0.16 Information Disclosure via Twig Sandbox Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-72698
Aliases: GHSA-p597-crqc-m349
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-72698
Type: osv

## Details
Grav CMS before 2.0.16 fails to filter system, site, and theme configuration arrays in sandboxed Twig renders, allowing content editors to read sensitive configuration values. Attackers with page-content edit access can access raw configuration arrays including secrets like cache credentials by using dot notation in Twig templates, bypassing the config_denied_paths restrictions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72698.json
- https://github.com/getgrav/grav/security/advisories/GHSA-p597-crqc-m349
- https://nvd.nist.gov/vuln/detail/CVE-2026-72698
- https://www.vulncheck.com/advisories/grav-cms-before-information-disclosure-via-twig-sandbox-bypass
