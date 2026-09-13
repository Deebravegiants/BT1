# [C] Grav CMS before 2.0.16 Origin Validation Bypass via Referer

## Summary
Severity: Critical
Advisory: CVE-2026-72702
Aliases: GHSA-9ccq-2jfg-qw33
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-72702
Type: osv

## Details
Grav CMS before 2.0.16 contains an origin validation bypass in the Uri::referrer() and Pages::referrerRoute() methods, which validate the Referer header using an unanchored string prefix match (str_starts_with($referrer, $base)) with no trailing delimiter. An attacker who controls a domain that begins with the victim site's origin (e.g. https://example.com.attacker.tld) can send a request with such a Referer to be treated as same-origin, bypassing the Referer-based origin check.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72702.json
- https://github.com/getgrav/grav/security/advisories/GHSA-9ccq-2jfg-qw33
- https://nvd.nist.gov/vuln/detail/CVE-2026-72702
- https://www.vulncheck.com/advisories/grav-cms-before-origin-validation-bypass-via-referer
