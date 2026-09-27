# [H] CVE-2017-7505

## Summary
Severity: High
Advisory: CVE-2017-7505
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-26
Source: https://osv.dev/vulnerability/CVE-2017-7505
Type: osv

## Details
Foreman since version 1.5 is vulnerable to an incorrect authorization check due to which users with user management permission who are assigned to some organization(s) can do all operations granted by these permissions on all administrator user object outside of their scope, such as editing global admin accounts including changing their passwords.

## References
- http://www.securityfocus.com/bid/98607
- http://projects.theforeman.org/issues/19612
- https://github.com/theforeman/foreman/pull/4545
