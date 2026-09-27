# [C] OpenEMR has an Unauthenticated MedEx Token Disclosure

## Summary
Severity: Critical
Advisory: CVE-2026-24898
Aliases: GHSA-qwff-3mw7-7rc7
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-03
Source: https://osv.dev/vulnerability/CVE-2026-24898
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to 8.0.0, an unauthenticated token disclosure vulnerability in the MedEx callback endpoint allows any unauthenticated visitor to obtain the practice's MedEx API tokens, leading to complete third-party service compromise, PHI exfiltration, unauthorized actions on the MedEx platform, and HIPAA violations. The vulnerability exists because the endpoint bypasses authentication ($ignoreAuth = true) and performs a MedEx login whenever $_POST['callback_key'] is provided, returning the full JSON response including sensitive API tokens. This vulnerability is fixed in 8.0.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24898.json
- https://github.com/openemr/openemr/security/advisories/GHSA-qwff-3mw7-7rc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-24898
- https://github.com/openemr/openemr/commit/8e4de59ab58222f13abc4e4040128737d857db9c
