# [H] CVE-2020-25031

## Summary
Severity: High
Advisory: CVE-2020-25031
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-31
Source: https://osv.dev/vulnerability/CVE-2020-25031
Type: osv

## Details
checkinstall 1.6.2, when used to create a package that contains a symlink, may trigger the creation of a mode 0777 executable file.

## References
- https://bugs.launchpad.net/ubuntu/+source/checkinstall/+bug/1861281
