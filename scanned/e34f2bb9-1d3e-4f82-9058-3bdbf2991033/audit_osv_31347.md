# [M] Unauthorized Access in danswer-ai/danswer

## Summary
Severity: Medium
Advisory: CVE-2024-9612
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-9612
Type: osv

## Details
In danswer-ai/danswer v0.3.94, administrators can set the visibility of pages within a workspace, including the search page. When the search page is set to be invisible, regular users cannot view the search page or access its functionalities from the front-end interface. However, the back-end does not verify the visibility status of the search page. Consequently, attackers can directly call the API to access the functionalities provided by the search page, bypassing the visibility restriction set by the administrator.

## References
- https://huntr.com/bounties/c1046fa0-a719-475e-ba62-2b97873fbac4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9612.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9612
