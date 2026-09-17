# [M] CVE-2021-37864

## Summary
Severity: Medium
Advisory: CVE-2021-37864
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-01-18
Source: https://osv.dev/vulnerability/CVE-2021-37864
Type: osv

## Details
Mattermost 6.1 and earlier fails to sufficiently validate permissions while viewing archived channels, which allows authenticated users to view contents of archived channels even when this is denied by system administrators by directly accessing the APIs.

## References
- https://mattermost.com/security-updates/
