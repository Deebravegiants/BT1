# [M] JLSEC-2026-500

## Summary
Severity: Medium
Advisory: JLSEC-2026-500
Ecosystem: Julia
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/JLSEC-2026-500
Type: osv

## Affected
- Julia: `pandoc_jll` — affected >=0 <3.1.9+0

## Details
Pandoc before 3.1.6 allows arbitrary file write: this can be triggered by providing a crafted image element in the input when generating files via the --extract-media option or outputting to PDF format. This allows an attacker to create or overwrite arbitrary files, depending on the privileges of the process running Pandoc. It only affects systems that pass untrusted user input to Pandoc and allow Pandoc to be used to produce a PDF or with the --extract-media option. NOTE: this issue exists because of an incomplete fix for CVE-2023-35936 (failure to properly account for double encoded path names).

## References
- https://github.com/jgm/pandoc/commit/eddedbfc14916aa06fc01ff04b38aeb30ae2e625
- https://github.com/jgm/pandoc/compare/3.1.5...3.1.6
- https://lists.debian.org/debian-lts-announce/2023/07/msg00029.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JGRJHU2FTSGTHHRTNDF7STEKLKKA25JN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LYP3FKDS3KAYMQUZVVL73IUI4CWSKLKP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QI6RBP6ZKVC2OOCV6SU2FUHPMAXDDJFU/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYP3FKDS3KAYMQUZVVL73IUI4CWSKLKP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QI6RBP6ZKVC2OOCV6SU2FUHPMAXDDJFU/
