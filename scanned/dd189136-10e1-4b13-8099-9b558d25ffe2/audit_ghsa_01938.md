# [H] Pillow denial of service

## Summary
Severity: High
Advisory: GHSA-g6rj-rv7j-xwp4
CVE: CVE-2021-28675
CWE: CWE-233, CWE-252
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-g6rj-rv7j-xwp4
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <8.2.0

## Details
An issue was discovered in Pillow before 8.2.0. `PSDImagePlugin.PsdImageFile` lacked a sanity check on the number of input layers relative to the size of the data block. This could lead to a DoS on `Image.open` prior to `Image.load`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28675
- https://github.com/python-pillow/Pillow/pull/5377/commits/22e9bee4ef225c0edbb9323f94c26cee0c623497
- https://github.com/advisories/GHSA-g6rj-rv7j-xwp4
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2021-139.yaml
- https://github.com/python-pillow/Pillow
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MQHA5HAIBOYI3R6HDWCLAGFTIQP767FL
- https://pillow.readthedocs.io/en/stable/releasenotes/8.2.0.html#cve-2021-28675-fix-dos-in-psdimageplugin
- https://security.gentoo.org/glsa/202107-33
