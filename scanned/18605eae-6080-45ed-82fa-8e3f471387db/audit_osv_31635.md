# [M] Insufficient Input Validation on Post Props

## Summary
Severity: Medium
Advisory: CVE-2025-20036
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2025-20036
Type: osv

## Details
Mattermost Mobile Apps versions <=2.22.0 fail to properly validate post props which allows a malicious authenticated user to cause a crash via a malicious post.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/20xxx/CVE-2025-20036.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-20036
