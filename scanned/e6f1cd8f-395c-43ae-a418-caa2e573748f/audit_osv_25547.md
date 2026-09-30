# [C] social-media-skeleton vulnerable to Pre-Auth SQLi leading to RCE

## Summary
Severity: Critical
Advisory: CVE-2023-39344
Aliases: GHSA-857x-p6fq-mgfh
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-08-04
Source: https://osv.dev/vulnerability/CVE-2023-39344
Type: osv

## Details
social-media-skeleton is an uncompleted social media project. A SQL injection vulnerability in the project allows UNION based injections, which indirectly leads to remote code execution. Commit 3cabdd35c3d874608883c9eaf9bf69b2014d25c1 contains a fix for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39344.json
- https://github.com/fobybus/social-media-skeleton/security/advisories/GHSA-857x-p6fq-mgfh
- https://nvd.nist.gov/vuln/detail/CVE-2023-39344
- https://github.com/fobybus/social-media-skeleton/commit/3cabdd35c3d874608883c9eaf9bf69b2014d25c1
