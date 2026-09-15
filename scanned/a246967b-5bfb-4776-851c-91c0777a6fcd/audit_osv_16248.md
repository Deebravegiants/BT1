# [M] CVE-2019-3825

## Summary
Severity: Medium
Advisory: CVE-2019-3825
CVSS: 6.4 (CVSS:3.0/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-06
Source: https://osv.dev/vulnerability/CVE-2019-3825
Type: osv

## Details
A vulnerability was discovered in gdm before 3.31.4. When timed login is enabled in configuration, an attacker could bypass the lock screen by selecting the timed login user and waiting for the timer to expire, at which time they would gain access to the logged-in user's session.

## References
- https://usn.ubuntu.com/3892-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3825
