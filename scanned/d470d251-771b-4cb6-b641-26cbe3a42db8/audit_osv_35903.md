# [M] Eclipse OpenJ9 : Method resolution default method precedence failure

## Summary
Severity: Medium
Advisory: CVE-2026-16441
Aliases: GHSA-hcfc-9hjx-2q7f
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:A/VC:N/VI:H/VA:L/SC:L/SI:H/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-16441
Type: osv

## Details
In Eclipse OpenJ9 versions up to 0.60, when executing class files where a previously concrete superclass method has been recompiled as abstract, execution is incorrectly delegated to an interface default method.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/194
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16441.json
- https://github.com/eclipse-openj9/openj9/security/advisories/GHSA-hcfc-9hjx-2q7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-16441
- https://github.com/eclipse-openj9/openj9/pull/24396
