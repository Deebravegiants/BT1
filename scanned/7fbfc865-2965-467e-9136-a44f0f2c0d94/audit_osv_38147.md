# [H] Combodo iTop: Access control bypass via OQL joins

## Summary
Severity: High
Advisory: CVE-2026-34948
Aliases: GHSA-cm4j-52rf-whgc
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-34948
Type: osv

## Details
Combodo iTop is a web based IT service management tool. Prior to 3.2.3, only classes present in the SELECT clause are protected by the silos access check in OQL. This issue has been fixed in version 3.2.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34948.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-cm4j-52rf-whgc
- https://nvd.nist.gov/vuln/detail/CVE-2026-34948
- https://github.com/Combodo/iTop/commit/e467ca83cfcfc5ba1f1d78a99d4805e595f114ba
