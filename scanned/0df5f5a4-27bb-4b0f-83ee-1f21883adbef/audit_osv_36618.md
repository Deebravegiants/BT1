# [M] Open eClass Business Logic Flaw Allows Students to Mark Attendance in Expired Activities

## Summary
Severity: Medium
Advisory: CVE-2026-24774
Aliases: GHSA-rv2x-4rc8-93jh
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-24774
Type: osv

## Details
The Open eClass platform (formerly known as GUnet eClass) is a complete course management system. Prior to version 4.2, a business logic vulnerability allows authenticated students to improperly mark themselves as present in attendance activities, including activities that have already expired, by directly accessing a crafted URL. This issue has been patched in version 4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24774.json
- https://github.com/gunet/openeclass/security/advisories/GHSA-rv2x-4rc8-93jh
- https://nvd.nist.gov/vuln/detail/CVE-2026-24774
