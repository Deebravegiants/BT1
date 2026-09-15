# [C] Numpy Deserialization of Untrusted Data

## Summary
Severity: Critical
Advisory: GHSA-9fq2-x9r6-wfmf
CVE: CVE-2019-6446
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9fq2-x9r6-wfmf
Type: github-advisory

## Affected
- PyPI: `numpy` — affected >=0 <1.16.3

## Details
** DISPUTED **  An issue was discovered in NumPy 1.16.2 and earlier. It uses the pickle Python module unsafely, which allows remote attackers to execute arbitrary code via a crafted serialized object, as demonstrated by a numpy.load call. NOTE: third parties dispute this issue because it is  a behavior that might have legitimate applications in (for example) loading serialized Python object arrays from trusted and authenticated sources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6446
- https://github.com/numpy/numpy/issues/12759
- https://github.com/numpy/numpy/pull/12889
- https://github.com/numpy/numpy/pull/13359
- https://github.com/numpy/numpy/commit/89b688732b37616c9d26623f81aaee1703c30ffb
- https://access.redhat.com/errata/RHSA-2019:3335
- https://access.redhat.com/errata/RHSA-2019:3704
- https://bugzilla.suse.com/show_bug.cgi?id=1122208
- https://github.com/advisories/GHSA-9fq2-x9r6-wfmf
- https://github.com/numpy/numpy
- https://github.com/pypa/advisory-database/tree/main/vulns/numpy/PYSEC-2019-108.yaml
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7ZZAYIQNUUYXGMKHSPEEXS4TRYFOUYE4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7ZZAYIQNUUYXGMKHSPEEXS4TRYFOUYE4
- https://web.archive.org/web/20210124234613/https://www.securityfocus.com/bid/106670
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00091.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00092.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00015.html
- http://www.securityfocus.com/bid/106670
