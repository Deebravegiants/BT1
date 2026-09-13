# [H] OpenCTI: Privilege escalation via graphQL API is abusable by organization admins, due to incorrect ACL on userEdit relationAdd

## Summary
Severity: High
Advisory: GHSA-q537-qhj4-wcjx
CVE: CVE-2026-44730
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-q537-qhj4-wcjx
Type: github-advisory

## Affected
- PyPI: `pycti` — affected >=0 <6.9.7

## Details
### Summary
An organization admin can escalate their privileges by adding a user from a different organization with higher privileges, to their own organization.

### Impact
Full platform access, access to sensitive or proprietary information.

## References
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-q537-qhj4-wcjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44730
- https://github.com/OpenCTI-Platform/opencti
- https://github.com/pypa/advisory-database/tree/main/vulns/pycti/PYSEC-2026-167.yaml
