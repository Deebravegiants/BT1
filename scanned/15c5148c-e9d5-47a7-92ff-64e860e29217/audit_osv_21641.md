# [M] CVE-2021-44692

## Summary
Severity: Medium
Advisory: CVE-2021-44692
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-01-26
Source: https://osv.dev/vulnerability/CVE-2021-44692
Type: osv

## Details
BuddyBoss Platform through 1.8.0 allows remote attackers to obtain the email address of each user. When creating a new user, it generates a Unique ID for their profile. This UID is their private email address with symbols removed and periods replaced with hyphens. For example. JohnDoe@example.com would become /members/johndoeexample-com and Jo.test@example.com would become /members/jo-testexample-com. The members list is available to everyone and (in a default configuration) often without authentication. It is therefore trivial to collect a list of email addresses.

## References
- https://www.buddyboss.com/resources/buddyboss-platform-releases/
- https://www.cygenta.co.uk/post/buddyboss
