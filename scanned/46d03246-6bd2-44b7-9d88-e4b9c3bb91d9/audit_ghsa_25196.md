# [C] XML Injection in ReportLab

## Summary
Severity: Critical
Advisory: GHSA-qpg2-vx7j-3869
CVE: CVE-2019-17626
CWE: CWE-91
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qpg2-vx7j-3869
Type: github-advisory

## Affected
- PyPI: `reportlab` — affected >=0 <3.5.28

## Details
ReportLab through 3.5.26 allows remote code execution because of toColor(eval(arg)) in colors.py, as demonstrated by a crafted XML document with '<span color="' followed by arbitrary Python code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17626
- https://www.debian.org/security/2020/dsa-4663
- https://web.archive.org/web/20191016111823/https://bitbucket.org/rptlab/reportlab/issues/199/eval-in-colorspy-leads-to-remote-code
- https://usn.ubuntu.com/4273-1
- https://security.netapp.com/advisory/ntap-20240719-0006
- https://security.gentoo.org/glsa/202007-35
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZZPHP2BJSTP4IYCSJRQINP763IHO6ASL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NSCTOE3DITFICY2XKBYZ5WAF5TSQ52DM
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZZPHP2BJSTP4IYCSJRQINP763IHO6ASL
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NSCTOE3DITFICY2XKBYZ5WAF5TSQ52DM
- https://lists.debian.org/debian-lts-announce/2020/02/msg00019.html
- https://hg.reportlab.com/hg-public/reportlab/rev/51a521ad7dd3
- https://github.com/pypa/advisory-database/tree/main/vulns/reportlab/PYSEC-2019-117.yaml
- https://github.com/advisories/GHSA-qpg2-vx7j-3869
- https://github.com/MrBitBucket/reportlab-mirror
- https://bitbucket.org/rptlab/reportlab/src/default/CHANGES.md
- https://bitbucket.org/rptlab/reportlab/issues/199/eval-in-colorspy-leads-to-remote-code
- https://access.redhat.com/security/cve/cve-2019-17626
- https://access.redhat.com/errata/RHSA-2020:0230
- https://access.redhat.com/errata/RHSA-2020:0201
