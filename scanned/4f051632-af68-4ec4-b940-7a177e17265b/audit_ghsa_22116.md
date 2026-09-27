# [H] Incorrect Default Permissions in Supervisor

## Summary
Severity: High
Advisory: GHSA-x7c8-4x3h-874w
CVE: CVE-2017-11610
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x7c8-4x3h-874w
Type: github-advisory

## Affected
- PyPI: `supervisor` — affected >=0 <3.0.1
- PyPI: `supervisor` — affected >=3.1.0 <3.1.4
- PyPI: `supervisor` — affected >=3.2.0 <3.2.4
- PyPI: `supervisor` — affected >=3.3.0 <3.3.3

## Details
The XML-RPC server in supervisor before 3.0.1, 3.1.x before 3.1.4, 3.2.x before 3.2.4, and 3.3.x before 3.3.3 allows remote authenticated users to execute arbitrary commands via a crafted XML-RPC request, related to nested supervisord namespace lookups.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11610
- https://github.com/Supervisor/supervisor/issues/964
- https://access.redhat.com/errata/RHSA-2017:3005
- https://github.com/Supervisor/supervisor
- https://github.com/Supervisor/supervisor/blob/3.0.1/CHANGES.txt
- https://github.com/Supervisor/supervisor/blob/3.1.4/CHANGES.txt
- https://github.com/Supervisor/supervisor/blob/3.2.4/CHANGES.txt
- https://github.com/Supervisor/supervisor/blob/3.3.3/CHANGES.txt
- https://github.com/advisories/GHSA-x7c8-4x3h-874w
- https://github.com/pypa/advisory-database/tree/main/vulns/supervisor/PYSEC-2017-41.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4GMSCGMM477N64Z3BM34RWYBGSLK466B
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DTPDZV4ZRICDYAYZVUHSYZAYDLRMG2IM
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JXGWOJNSWWK2TTWQJZJUP66FLFIWDMBQ
- https://security.gentoo.org/glsa/201709-06
- https://www.exploit-db.com/exploits/42779
- http://www.debian.org/security/2017/dsa-3942
