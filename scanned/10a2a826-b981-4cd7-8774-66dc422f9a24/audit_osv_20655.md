# [H] CVE-2021-3575

## Summary
Severity: High
Advisory: CVE-2021-3575
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-04
Source: https://osv.dev/vulnerability/CVE-2021-3575
Type: osv

## Details
A heap-based buffer overflow was found in openjpeg in color.c:379:42 in sycc420_to_rgb when decompressing a crafted .j2k file. An attacker could use this to execute arbitrary code with the permissions of the application compiled against openjpeg.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZ54FGM2IGAP4AWSJ22JKHOPHCR3FGYU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QB6AI7CWXWMEDZIQY4LQ6DMIEXMDOHUP/
- https://ubuntu.com/security/CVE-2021-3575
- https://bugzilla.redhat.com/show_bug.cgi?id=1957616
- https://github.com/uclouvain/openjpeg/issues/1347
