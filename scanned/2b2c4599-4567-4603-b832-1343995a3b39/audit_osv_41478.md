# [M] Grav before 2.0.2 Config Exfiltration via offsetGet Filter

## Summary
Severity: Medium
Advisory: CVE-2026-61450
Aliases: CVE-2026-61842, GHSA-mc5q-6hpj-rp7j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-61450
Type: osv

## Details
Grav before 2.0.2 contains a Twig sandbox bypass that allows a page author (any admin.pages user, or anyone able to write to user/pages) to exfiltrate configuration secrets. Although the sandbox replaces the 'config' variable with a redacted facade and strips Config::get/toArray from the method allowlist, the raw container remains accessible via the allow-listed grav.offsetGet('config'), which returns the real Config object. Allow-listed object-dumping filters (json_encode, print_r, yaml_encode) then serialize that object at the PHP level without invoking the sandbox method gate, exposing the full config tree including plugin secrets such as SMTP credentials, API keys, and plugin DB credentials. This is an incomplete fix for GHSA-j274-39qw-32c9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61450.json
- https://github.com/getgrav/grav/security/advisories/GHSA-mc5q-6hpj-rp7j
- https://nvd.nist.gov/vuln/detail/CVE-2026-61450
- https://www.vulncheck.com/advisories/grav-before-config-exfiltration-via-offsetget-filter
