# [M] CVE-2026-18744

## Summary
Severity: Medium
Advisory: CVE-2026-18744
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-18744
Type: osv

## Details
Any authenticated case participant can fetch any OTHER vendor's CaseStatement + per-vul CaseMemberStatus by supplying that member's id — test_func only checks _is_my_case, not ownership of kwargs['member']. Bypasses share_status; leaks embargoed vendor affected/not-affected + statement text cross-tenant.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18744.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18744
- https://github.com/CERTCC/VINCE/pull/235
- https://github.com/CERTCC/VINCE
