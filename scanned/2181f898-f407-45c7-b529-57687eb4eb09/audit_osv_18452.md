# [C] CVE-2020-27780

## Summary
Severity: Critical
Advisory: CVE-2020-27780
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-18
Source: https://osv.dev/vulnerability/CVE-2020-27780
Type: osv

## Details
A flaw was found in Linux-Pam in versions prior to 1.5.1 in the way it handle empty passwords for non-existing users. When the user doesn't exist PAM try to authenticate with root and in the case of an empty password it successfully authenticate.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1901094
