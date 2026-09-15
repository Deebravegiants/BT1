# [C] CVE-2020-7245

## Summary
Severity: Critical
Advisory: CVE-2020-7245
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-23
Source: https://osv.dev/vulnerability/CVE-2020-7245
Type: osv

## Details
Incorrect username validation in the registration process of CTFd v2.0.0 - v2.2.2 allows an attacker to take over an arbitrary account if the username is known and emails are enabled on the CTFd instance. To exploit the vulnerability, one must register with a username identical to the victim's username, but with white space inserted before and/or after the username. This will register the account with the same username as the victim. After initiating a password reset for the new account, CTFd will reset the victim's account password due to the username collision.

## References
- https://github.com/CTFd/CTFd/pull/1218
- https://github.com/CTFd/CTFd/releases/tag/2.2.3
