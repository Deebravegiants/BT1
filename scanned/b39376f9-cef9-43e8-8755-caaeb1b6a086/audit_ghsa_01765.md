# [H] Double Free in psutil

## Summary
Severity: High
Advisory: GHSA-qfc5-mcwq-26q8
CVE: CVE-2019-18874
CWE: CWE-415
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-03-12
Source: https://github.com/advisories/GHSA-qfc5-mcwq-26q8
Type: github-advisory

## Affected
- PyPI: `psutil` — affected >=0 <5.6.6

## Details
psutil (aka python-psutil) through 5.6.5 can have a double free. This occurs because of refcount mishandling within a while or for loop that converts system data into a Python object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18874
- https://github.com/giampaolo/psutil/pull/1616
- https://github.com/giampaolo/psutil/commit/7d512c8e4442a896d56505be3e78f1156f443465
- https://github.com/advisories/GHSA-qfc5-mcwq-26q8
- https://github.com/giampaolo/psutil
- https://github.com/giampaolo/psutil/blob/master/HISTORY.rst#566
- https://github.com/pypa/advisory-database/tree/main/vulns/psutil/PYSEC-2019-41.yaml
- https://lists.debian.org/debian-lts-announce/2019/11/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2P7QI7MOTZTFXQYU23CP3RAWXCERMOAS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OLETTJYZL2SMBUI4Q2NGBMGPDPP54SRG
- https://usn.ubuntu.com/4204-1
