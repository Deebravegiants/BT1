# [M] CVE-2022-46890

## Summary
Severity: Medium
Advisory: CVE-2022-46890
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-01-19
Source: https://osv.dev/vulnerability/CVE-2022-46890
Type: osv

## Details
Weak access control in NexusPHP before 1.7.33 allows a remote authenticated user to edit any post in the forum (this is caused by a lack of checks performed by the /forums.php?action=post page).

## References
- https://github.com/xiaomlove/nexusphp/releases/tag/v1.7.33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46890.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46890
- https://www.surecloud.com/resources/blog/nexusphp-surecloud-security-review-identifies-authenticated-unauthenticated-vulnerabilities
