# [M] CVE-2019-20485

## Summary
Severity: Medium
Advisory: CVE-2019-20485
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-19
Source: https://osv.dev/vulnerability/CVE-2019-20485
Type: osv

## Details
qemu/qemu_driver.c in libvirt before 6.0.0 mishandles the holding of a monitor job during a query to a guest agent, which allows attackers to cause a denial of service (API blockage).

## References
- https://libvirt.org/git/?p=libvirt.git%3Ba=commit%3Bh=a663a860819287e041c3de672aad1d8543098ecc
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D5GE6ISYUL3CIWO3FQRUGMKTKP2NYED2/
- https://www.mail-archive.com/debian-bugs-dist%40lists.debian.org/msg1730509.html
- https://security-tracker.debian.org/tracker/CVE-2019-20485
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=953078
- https://bugzilla.redhat.com/show_bug.cgi?id=1809740
