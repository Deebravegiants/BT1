# [C] WBCE CMS is Vulnerable to Privilege Escalation via Group ID Manipulation (IDOR)

## Summary
Severity: Critical
Advisory: CVE-2025-65094
Aliases: GHSA-hmmw-4ccm-fx44
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-65094
Type: osv

## Details
WBCE CMS is a content management system. Prior to version 1.6.4, a low-privileged user in WBCE CMS can escalate their privileges to the Administrators group by manipulating the groups[] parameter in the /admin/users/save.php request. The UI restricts users to assigning only their existing group, but server-side validation is missing, allowing attackers to overwrite their group membership and obtain full administrative access. This results in a complete compromise of the CMS. This issue has been patched in version 1.6.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65094.json
- https://github.com/WBCE/WBCE_CMS/security/advisories/GHSA-hmmw-4ccm-fx44
- https://nvd.nist.gov/vuln/detail/CVE-2025-65094
- https://github.com/WBCE/WBCE_CMS/commit/96046178f4c80cf16f7c224054dec7fdadddda7e
