# [H] CVE-2017-14163

## Summary
Severity: High
Advisory: CVE-2017-14163
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-31
Source: https://osv.dev/vulnerability/CVE-2017-14163
Type: osv

## Details
An issue was discovered in Mahara before 15.04.14, 16.x before 16.04.8, 16.10.x before 16.10.5, and 17.x before 17.04.3. When one closes the browser without logging out of Mahara, the value in the usr_session table is not removed. If someone were to open a browser, visit the Mahara site, and adjust the 'mahara' cookie to the old value, they can get access to the user's account.

## References
- https://bugs.launchpad.net/mahara/+bug/1701978
