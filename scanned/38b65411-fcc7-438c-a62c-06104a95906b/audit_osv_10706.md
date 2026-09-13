# [H] CVE-2017-18376

## Summary
Severity: High
Advisory: CVE-2017-18376
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-02
Source: https://osv.dev/vulnerability/CVE-2017-18376
Type: osv

## Details
An improper authorization check in the User API in TheHive before 2.13.4 and 3.x before 3.3.1 allows users with read-only or read/write access to escalate their privileges to the administrator's privileges. This affects app/controllers/UserCtrl.scala.

## References
- https://gist.github.com/RaJiska/c1b4521aefd77ed43b06045ca05e2591
- https://github.com/TheHive-Project/TheHive/releases/tag/3.3.1
- https://github.com/TheHive-Project/TheHive/issues/408
