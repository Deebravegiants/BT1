# [M] CVE-2021-42373

## Summary
Severity: Medium
Advisory: CVE-2021-42373
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-15
Source: https://osv.dev/vulnerability/CVE-2021-42373
Type: osv

## Details
A NULL pointer dereference in Busybox's man applet leads to denial of service when a section name is supplied but no page argument is given

## References
- https://claroty.com/team82/research/unboxing-busybox-14-vulnerabilities-uncovered-by-claroty-jfrog
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6T2TURBYYJGBMQTTN2DSOAIQGP7WCPGV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UQXGOGWBIYWOIVXJVRKHZR34UMEHQBXS/
- https://jfrog.com/blog/unboxing-busybox-14-new-vulnerabilities-uncovered-by-claroty-and-jfrog/
- https://security.netapp.com/advisory/ntap-20211223-0002/
