# [C] CVE-2024-46918

## Summary
Severity: Critical
Advisory: CVE-2024-46918
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-15
Source: https://osv.dev/vulnerability/CVE-2024-46918
Type: osv

## Details
app/Controller/UserLoginProfilesController.php in MISP before 2.4.198 does not prevent an org admin from viewing sensitive login fields of another org admin in the same org.

## References
- https://github.com/MISP/MISP/compare/v2.4.197...v2.4.198
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46918.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46918
- https://github.com/MISP/MISP/commit/3a5227d7b3d4518ac109af61979a00145a0de6fa
