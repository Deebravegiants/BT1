# [H] Pillow denial of service via PNG bomb

## Summary
Severity: High
Advisory: GHSA-h5rf-vgqx-wjv2
CVE: CVE-2014-9601
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-h5rf-vgqx-wjv2
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <2.7.0

## Details
Pillow before 2.7.0 allows remote attackers to cause a denial of service via a compressed text chunk in a PNG image that has a large size when it is decompressed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9601
- https://github.com/python-pillow/Pillow/pull/1060
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2015-16.yaml
- https://github.com/python-pillow/Pillow
- https://web.archive.org/web/20200227221255/http://www.securityfocus.com/bid/77758
- https://www.djangoproject.com/weblog/2015/jan/02/pillow-security-release
- http://lists.fedoraproject.org/pipermail/package-announce/2015-January/148442.html
- http://lists.opensuse.org/opensuse-updates/2015-04/msg00056.html
- http://pillow.readthedocs.org/releasenotes/2.7.0.html
- http://www.oracle.com/technetwork/topics/security/bulletinjul2015-2511963.html
