# [H] knowns through 0.33.0 Authorization Bypass via project.set Bootstrap Exemption

## Summary
Severity: High
Advisory: CVE-2026-88939
Aliases: CVE-2026-88940, GHSA-h73x-698r-qrvg
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88939
Type: osv

## Details
knowns through 0.33.0 exempts the project.set action from permission guard checks unconditionally, allowing read-only agent sessions to bypass restrictions. Attackers can invoke project.set to repoint the server at another project directory and obtain write access capabilities.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88939.json
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-h73x-698r-qrvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-88939
- https://www.vulncheck.com/advisories/knowns-through-0.33.0-authorization-bypass-via-project-set-bootstrap-exemption
- https://github.com/knowns-dev/knowns/blob/v0.33.0/internal/permissions/guard.go#L104-L113
- https://github.com/knowns-dev/knowns/blob/v0.33.0/internal/permissions/registry.go#L51-L54
