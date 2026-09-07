# [C] Exposure of Sensitive Information to an Unauthorized Actor in urllib3

## Summary
Severity: Critical
Advisory: GHSA-www2-v7xj-xrc6
CVE: CVE-2018-20060
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-12
Source: https://github.com/advisories/GHSA-www2-v7xj-xrc6
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=0 <1.23

## Details
urllib3 before version 1.23 does not remove the Authorization HTTP header when following a cross-origin redirect (i.e., a redirect that differs in host, port, or scheme). This can allow for credentials in the Authorization header to be exposed to unintended hosts or transmitted in cleartext.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20060
- https://github.com/urllib3/urllib3/issues/1316
- https://github.com/urllib3/urllib3/pull/1346
- https://github.com/urllib3/urllib3/commit/560bd227b90f74417ffaedebf5f8d05a8ee4f532
- https://usn.ubuntu.com/3990-1
- https://security.netapp.com/advisory/ntap-20241227-0010
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XWP36YW3KSVLXDBY3QJKDYEPCIMN3VQZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BXLAXHM3Z6DUCXZ7ZXZ2EAYJXWDCZFCT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5SJERZEJDSUYQP7BNBXMBHRHGY26HRZD
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XWP36YW3KSVLXDBY3QJKDYEPCIMN3VQZ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BXLAXHM3Z6DUCXZ7ZXZ2EAYJXWDCZFCT
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5SJERZEJDSUYQP7BNBXMBHRHGY26HRZD
- https://lists.debian.org/debian-lts-announce/2021/06/msg00015.html
- https://github.com/urllib3/urllib3/blob/master/CHANGES.rst
- https://github.com/urllib3/urllib3
- https://github.com/pypa/advisory-database/tree/main/vulns/urllib3/PYSEC-2018-32.yaml
- https://bugzilla.redhat.com/show_bug.cgi?id=1649153
- https://access.redhat.com/errata/RHSA-2019:2272
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00039.html
