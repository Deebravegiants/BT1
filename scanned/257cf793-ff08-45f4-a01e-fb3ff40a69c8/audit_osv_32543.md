# [M] CVE-2025-32360

## Summary
Severity: Medium
Advisory: CVE-2025-32360
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-04-05
Source: https://osv.dev/vulnerability/CVE-2025-32360
Type: osv

## Details
In Zammad 6.4.x before 6.4.2, there is information exposure. Only agents should be able to see and work on shared article drafts. However, a logged in customer was able to see details about shared drafts for their customer tickets in the browser console, which may contain confidential information, and also to manipulate them via API.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32360.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32360
- https://zammad.com/en/advisories/zaa-2025-03
