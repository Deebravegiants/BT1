# [C] CVE-2019-15149

## Summary
Severity: Critical
Advisory: CVE-2019-15149
Aliases: GHSA-8rf6-w2mx-4xjh, PYSEC-2019-104
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-18
Source: https://osv.dev/vulnerability/CVE-2019-15149
Type: osv

## Details
core.py in Mitogen before 0.2.8 has a typo that drops the unidirectional-routing protection mechanism in the case of a child that is initiated by another child. The Ansible extension is unaffected. NOTE: the vendor disputes this issue because it is exploitable only in conjunction with hypothetical other factors, i.e., an affected use case within a library caller, and a bug in the message receiver policy code that led to reliance on this extra protection mechanism

## References
- https://mitogen.networkgenomics.com/changelog.html#v0-2-8-2019-08-18
- https://github.com/dw/mitogen/commit/5924af1566763e48c42028399ea0cd95c457b3dc
