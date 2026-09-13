# [C] OpenProject: SQL injection in timestamps functionality

## Summary
Severity: Critical
Advisory: CVE-2026-52785
Aliases: GHSA-98vw-2r87-fx2r
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-52785
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.3.3 and 17.4.1, there is a SQL injection in timestamps functionality. OpenProject baseline comparison allows callers to request historic work-package attributes using the timestamps parameter. This vulnerability is fixed in 17.3.3 and 17.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52785.json
- https://github.com/opf/openproject/security/advisories/GHSA-98vw-2r87-fx2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-52785
