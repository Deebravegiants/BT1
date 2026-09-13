# [M] CVE-2018-7169

## Summary
Severity: Medium
Advisory: CVE-2018-7169
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-02-15
Source: https://osv.dev/vulnerability/CVE-2018-7169
Type: osv

## Details
An issue was discovered in shadow 4.5. newgidmap (in shadow-utils) is setuid and allows an unprivileged user to be placed in a user namespace where setgroups(2) is permitted. This allows an attacker to remove themselves from a supplementary group, which may allow access to certain filesystem paths if the administrator has used "group blacklisting" (e.g., chmod g-rwx) to restrict access to paths. This flaw effectively reverts a security feature in the kernel (in particular, the /proc/self/setgroups knob) to prevent this sort of privilege escalation.

## References
- https://security.gentoo.org/glsa/201805-09
- https://bugs.launchpad.net/ubuntu/+source/shadow/+bug/1729357
