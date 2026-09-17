# [C] CVE-2021-42377

## Summary
Severity: Critical
Advisory: CVE-2021-42377
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-15
Source: https://osv.dev/vulnerability/CVE-2021-42377
Type: osv

## Details
An attacker-controlled pointer free in Busybox's hush applet leads to denial of service and possible code execution when processing a crafted shell command, due to the shell mishandling the &&& string. This may be used for remote code execution under rare conditions of filtered command input.

## References
- https://claroty.com/team82/research/unboxing-busybox-14-vulnerabilities-uncovered-by-claroty-jfrog
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6T2TURBYYJGBMQTTN2DSOAIQGP7WCPGV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UQXGOGWBIYWOIVXJVRKHZR34UMEHQBXS/
- https://jfrog.com/blog/unboxing-busybox-14-new-vulnerabilities-uncovered-by-claroty-and-jfrog/
- https://security.netapp.com/advisory/ntap-20211223-0002/
