# [M] CVE-2020-27837

## Summary
Severity: Medium
Advisory: CVE-2020-27837
CVSS: 6.4 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-28
Source: https://osv.dev/vulnerability/CVE-2020-27837
Type: osv

## Details
A flaw was found in GDM in versions prior to 3.38.2.1. A race condition in the handling of session shutdown makes it possible to bypass the lock screen for a user that has autologin enabled, accessing their session without authentication. This is similar to CVE-2017-12164, but requires more difficult conditions to exploit.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1906812
