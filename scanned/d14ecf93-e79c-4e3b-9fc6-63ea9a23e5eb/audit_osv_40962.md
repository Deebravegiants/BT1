# [M] Capgo - Org/App Scope Mismatch in Device Creation Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-56320
Aliases: GHSA-mhrc-qhq8-872f
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-56320
Type: osv

## Details
Capgo before 12.128.2 contains an authorization flaw in POST /private/create_device that accepts a caller-supplied org_id parameter without validating it matches the target app's owner organization. Authenticated attackers can create device records for an application using a foreign organization identifier, bypassing the intended org/app authorization boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56320.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-mhrc-qhq8-872f
- https://nvd.nist.gov/vuln/detail/CVE-2026-56320
- https://www.vulncheck.com/advisories/capgo-org-app-scope-mismatch-in-device-creation-endpoint
