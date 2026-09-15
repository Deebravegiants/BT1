# [H] BIT-pillow-2021-28677

## Summary
Severity: High
Advisory: BIT-pillow-2021-28677
Aliases: CVE-2021-28677, GHSA-q5hq-fp76-qmrc, PYSEC-2021-93
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-pillow-2021-28677
Type: osv

## Affected
- Bitnami: `pillow` — affected >=0 <8.2.0

## Details
An issue was discovered in Pillow before 8.2.0. For EPS data, the readline implementation used in EPSImageFile has to deal with any combination of \r and \n as line endings. It used an accidentally quadratic method of accumulating lines while looking for a line ending. A malicious EPS file could use this to perform a DoS of Pillow in the open phase, before an image was accepted for opening.

## References
- https://github.com/python-pillow/Pillow/pull/5377
- https://lists.debian.org/debian-lts-announce/2021/07/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MQHA5HAIBOYI3R6HDWCLAGFTIQP767FL/
- https://pillow.readthedocs.io/en/stable/releasenotes/8.2.0.html#cve-2021-28677-fix-eps-dos-on-open
- https://security.gentoo.org/glsa/202107-33
- https://nvd.nist.gov/vuln/detail/CVE-2021-28677
