# [H] CVE-2014-0144

## Summary
Severity: High
Advisory: CVE-2014-0144
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-09-29
Source: https://osv.dev/vulnerability/CVE-2014-0144
Type: osv

## Details
QEMU before 2.0.0 block drivers for CLOOP, QCOW2 version 2 and various other image formats are vulnerable to potential memory corruptions, integer/buffer overflows or crash caused by missing input validations which could allow a remote user to execute arbitrary code on the host with the privileges of the QEMU process.

## References
- http://rhn.redhat.com/errata/RHSA-2014-0420.html
- http://rhn.redhat.com/errata/RHSA-2014-0421.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1079240
- https://bugzilla.redhat.com/show_bug.cgi?id=1079240
- https://bugzilla.redhat.com/show_bug.cgi?id=1079240
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=24342f2cae47d03911e346fe1e520b00dc2818e0
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=2d51c32c4b511db8bb9e58208f1e2c25e4c06c85
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=5dab2faddc8eaa1fb1abdbe2f502001fc13a1b21
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=63fa06dc978f3669dbfd9443b33cde9e2a7f4b41
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=6d4b9e55fc625514a38d27cff4b9933f617fa7dc
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=7b103b36d6ef3b11827c203d3a793bf7da50ecd6
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=97f1c45c6f456572e5b504b8614e4a69e23b8e3a
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=a1b3955c9415b1e767c130a2f59fee6aa28e575b
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=ce48f2f441ca98885267af6fd636a7cb804ee646
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=d65f97a82c4ed48374a764c769d4ba1ea9724e97
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=f56b9bc3ae20fc93815b34aa022be919941406ce
- https://www.vulnerabilitycenter.com/#%21vul=44767
