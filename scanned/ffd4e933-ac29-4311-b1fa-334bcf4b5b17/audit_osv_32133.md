# [M] Disclosure of Sensitive User Information via API in reNgine

## Summary
Severity: Medium
Advisory: CVE-2025-24899
Aliases: GHSA-r3fp-xr9f-wv38
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-02-03
Source: https://osv.dev/vulnerability/CVE-2025-24899
Type: osv

## Details
reNgine is an automated reconnaissance framework for web applications. A vulnerability was discovered in reNgine, where **an insider attacker with any role** (such as Auditor, Penetration Tester, or Sys Admin) **can extract sensitive information from other reNgine users.** After running a scan and obtaining vulnerabilities from a target, the attacker can retrieve details such as `username`, `password`, `email`, `role`, `first name`, `last name`, `status`, and `activity information` by making a GET request to `/api/listVulnerability/`. This issue has been addressed in version 2.2.0 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24899.json
- https://github.com/yogeshojha/rengine/security/advisories/GHSA-r3fp-xr9f-wv38
- https://nvd.nist.gov/vuln/detail/CVE-2025-24899
- https://github.com/yogeshojha/rengine/commit/a658b8519f1a3347634b04733cf91ed933af1f99
