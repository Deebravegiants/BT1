# [M] CVE-2016-7078

## Summary
Severity: Medium
Advisory: CVE-2016-7078
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-09-10
Source: https://osv.dev/vulnerability/CVE-2016-7078
Type: osv

## Details
foreman before version 1.15.0 is vulnerable to an information leak through organizations and locations feature. When a user is assigned _no_ organizations/locations, they are able to view all resources instead of none (mirroring an administrator's view). The user's actions are still limited by their assigned permissions, e.g. to control viewing, editing and deletion.

## References
- http://www.securityfocus.com/bid/96385
- https://github.com/theforeman/foreman/commit/5f606e11cf39719bf62f8b1f3396861b32387905
- https://projects.theforeman.org/issues/16982
- https://seclists.org/oss-sec/2017/q1/470
- https://theforeman.org/security.html#2016-7078
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-7078
