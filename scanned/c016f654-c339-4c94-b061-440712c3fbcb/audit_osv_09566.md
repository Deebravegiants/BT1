# [C] CVE-2017-1000152

## Summary
Severity: Critical
Advisory: CVE-2017-1000152
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-03
Source: https://osv.dev/vulnerability/CVE-2017-1000152
Type: osv

## Details
Mahara 15.04 before 15.04.7 and 15.10 before 15.10.3 running PHP 5.3 are vulnerable to one user being logged in as another user on a separate computer as the same session ID is served. This situation can occur when a user takes an action that forces another user to be logged out of Mahara, such as an admin changing another user's account settings.

## References
- https://bugs.launchpad.net/mahara/+bug/1570744
