# [H] CVE-2015-8378

## Summary
Severity: High
Advisory: CVE-2015-8378
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-04-10
Source: https://osv.dev/vulnerability/CVE-2015-8378
Type: osv

## Details
In KeePassX before 0.4.4, a cleartext copy of password data is created upon a cancel of an XML export action. This allows context-dependent attackers to obtain sensitive information by reading the .xml dotfile.

## References
- http://bugs.debian.org/791858
- https://www.keepassx.org/changelog
- http://bugs.debian.org/791858
