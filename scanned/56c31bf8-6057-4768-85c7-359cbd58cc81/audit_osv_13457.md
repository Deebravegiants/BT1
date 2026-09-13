# [M] CVE-2018-19976

## Summary
Severity: Medium
Advisory: CVE-2018-19976
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-12-17
Source: https://osv.dev/vulnerability/CVE-2018-19976
Type: osv

## Details
In YARA 3.8.1, bytecode in a specially crafted compiled rule is exposed to information about its environment, in libyara/exec.c. This is a consequence of the design of the YARA virtual machine.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DFFXDAMP6GJ337LIOTVF5I4T6QGMN3ZR/
- https://github.com/VirusTotal/yara/issues/999
- https://bnbdr.github.io/posts/extracheese/
- https://github.com/bnbdr/swisscheese/
