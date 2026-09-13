# [C] Project restriction bypass via instance migration config override

## Summary
Severity: Critical
Advisory: CVE-2026-63296
Aliases: GHSA-gcr9-5q6r-w625
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-63296
Type: osv

## Details
An authorization bypass vulnerability in LXD allows an authenticated attacker to bypass target project restrictions during instance migration. When migrating an instance to a target project, LXD accepts configuration overrides without validating the new configuration against the target project's enforced restrictions. An attacker can exploit this flaw to move instances with disallowed high-privilege configurations into restricted projects, bypassing security controls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63296.json
- https://github.com/canonical/lxd/security/advisories/GHSA-gcr9-5q6r-w625
- https://nvd.nist.gov/vuln/detail/CVE-2026-63296
- https://github.com/canonical/lxd
