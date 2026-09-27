# [M] Team Creator's Email Address is disclosed to Team Members via one of the APIs

## Summary
Severity: Medium
Advisory: CVE-2022-0708
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-02-21
Source: https://osv.dev/vulnerability/CVE-2022-0708
Type: osv

## Details
Mattermost 6.3.0 and earlier fails to protect email addresses of the creator of the team via one of the APIs, which allows authenticated team members to access this information resulting in sensitive & private information disclosure.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0708.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-0708
