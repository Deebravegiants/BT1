# [M] CVE-2019-9644

## Summary
Severity: Medium
Advisory: CVE-2019-9644
Aliases: GHSA-hhx8-cr55-qcxx, PYSEC-2019-159, PYSEC-2026-2531
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2019-03-12
Source: https://osv.dev/vulnerability/CVE-2019-9644
Type: osv

## Details
An XSSI (cross-site inclusion) vulnerability in Jupyter Notebook before 5.7.6 allows inclusion of resources on malicious pages when visited by users who are authenticated with a Jupyter server. Access to the content of resources has been demonstrated with Internet Explorer through capturing of error messages, though not reproduced with other browsers. This occurs because Internet Explorer's error messages can include the content of any invalid JavaScript that was encountered.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UP5RLEES2JBBNSNLBR65XM6PCD4EMF7D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VMDPJBVXOVO6LYGAT46VZNHH6JKSCURO/
- https://github.com/jupyter/notebook/compare/f3f00df...05aa4b2
