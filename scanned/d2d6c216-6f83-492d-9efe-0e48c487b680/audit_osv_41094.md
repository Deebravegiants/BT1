# [C] Pagekit CMS 1.0.18 Privilege Escalation via UserApiController

## Summary
Severity: Critical
Advisory: CVE-2026-57518
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-57518
Type: osv

## Details
Pagekit CMS 1.0.18 contains a privilege escalation vulnerability that allows authenticated users with the 'user: manage users' permission to escalate privileges by assigning arbitrary custom roles to themselves due to missing authorization checks in UserApiController::saveAction(). Attackers can assign themselves a custom role with the 'system: manage packages' permission and then upload and install a malicious PHP package through the admin package installer to achieve remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57518.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57518
- https://www.vulncheck.com/advisories/pagekit-cms-privilege-escalation-via-userapicontroller
- https://github.com/pagekit/pagekit
- https://gist.github.com/sermikr0/6f0a67e9d101746fcdb04827de137847
