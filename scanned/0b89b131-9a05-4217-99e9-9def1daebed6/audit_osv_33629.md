# [C] Emlog Pro Contains a File Upload Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-47787
Aliases: GHSA-4mcj-8gvh-p753
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-05-15
Source: https://osv.dev/vulnerability/CVE-2025-47787
Type: osv

## Details
Emlog is an open source website building system. Emlog Pro prior to version 2.5.10 contains a file upload vulnerability. The store.php component contains a critical security flaw where it fails to properly validate the contents of remotely downloaded ZIP plugin files. This insufficient validation allows attackers to execute arbitrary code on the vulnerable system. Version 2.5.10 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47787.json
- https://github.com/emlog/emlog/security/advisories/GHSA-4mcj-8gvh-p753
- https://nvd.nist.gov/vuln/detail/CVE-2025-47787
- https://github.com/emlog/emlog/commit/691c13e90df2fb35e120f4e0735078bad018eed7
