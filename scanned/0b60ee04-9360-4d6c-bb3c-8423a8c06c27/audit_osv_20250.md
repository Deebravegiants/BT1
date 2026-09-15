# [M] CVE-2021-32613

## Summary
Severity: Medium
Advisory: CVE-2021-32613
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-14
Source: https://osv.dev/vulnerability/CVE-2021-32613
Type: osv

## Details
In radare2 through 5.3.0 there is a double free vulnerability in the pyc parse via a crafted file which can lead to DoS.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W3LPB5VGCIA7WA55FSB3YZQFUGZKWD7O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y3S7JB46PONPHXZHIMR2XDPLGJCN5ZIX/
- https://bugzilla.redhat.com/show_bug.cgi?id=1959939
- https://github.com/radareorg/radare2/commit/5e16e2d1c9fe245e4c17005d779fde91ec0b9c05
- https://github.com/radareorg/radare2/commit/a07dedb804a82bc01c07072861942dd80c6b6d62
- https://github.com/radareorg/radare2/issues/18666
- https://github.com/radareorg/radare2/issues/18667
- https://github.com/radareorg/radare2/issues/18679
