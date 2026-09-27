# [M] CVE-2024-42988

## Summary
Severity: Medium
Advisory: CVE-2024-42988
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-42988
Type: osv

## Details
Lack of access control in ChallengeSolves (/api/v1/challenges/<challenge id>/solves) of CTFd v2.0.0 - v3.7.2 allows authenticated users to retrieve a list of users who have solved the challenge, regardless of the Account Visibility settings. The issue is fixed in v3.7.3+.

## References
- https://github.com/CTFd/CTFd/releases/tag/3.7.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42988.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42988
- https://github.com/CTFd/CTFd/pull/2570
- https://blog.ctfd.io/ctfd-3-7-3/
