# [C] CVE-2021-20204

## Summary
Severity: Critical
Advisory: CVE-2021-20204
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2021-20204
Type: osv

## Details
A heap memory corruption problem (use after free) can be triggered in libgetdata v0.10.0 when processing maliciously crafted dirfile databases. This degrades the confidentiality, integrity and availability of third-party software that uses libgetdata as a library. This vulnerability may lead to arbitrary code execution or privilege escalation depending on input/skills of attacker.

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/43JTGEMYMCTHD3LHFD7ENBNSWCNBCYEY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GB7T7DW7XRPJOUE25ZE7GF244FPCHBWY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OE23HBLIVKVPOQ5MVADWPOCFMREVF4QZ/
- https://bugzilla.redhat.com/show_bug.cgi?id=1956348
