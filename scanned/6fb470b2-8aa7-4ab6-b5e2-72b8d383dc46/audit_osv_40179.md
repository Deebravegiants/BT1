# [H] Apache Atlas: Missing Authorization on Admin Endpoints

## Summary
Severity: High
Advisory: CVE-2026-50622
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-50622
Type: osv

## Details
Description:
Missing Authorization in Apache Atlas.
A missing authorization vulnerability in Apache Atlas's admin endpoints allows any authenticated user, regardless of their assigned role, to perform administrative operations.




Affect Version:
This issue affects Apache Atlas: from 0.8 through 2.5.0.


Mitigation:
Users are recommended to upgrade to version 2.6.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/29/1
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50622.json
- https://lists.apache.org/thread/6r9vs7g5gkp983pwvky781hofdozhgzn
- https://nvd.nist.gov/vuln/detail/CVE-2026-50622
