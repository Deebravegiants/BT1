# [M] Insufficient Verification of Data Authenticity in Pillow

## Summary
Severity: Medium
Advisory: GHSA-hjfx-8p6c-g7gx
CVE: CVE-2021-28678
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-hjfx-8p6c-g7gx
Type: github-advisory

## Affected
- PyPI: `Pillow` — affected >=5.1.0 <8.2.0

## Details
An issue was discovered in Pillow before 8.2.0. For BLP data, BlpImagePlugin did not properly check that reads (after jumping to file offsets) returned data. This could lead to a DoS where the decoder could be run a large number of times on empty data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28678
- https://github.com/python-pillow/Pillow/pull/5377
- https://github.com/python-pillow/Pillow/pull/5377/commits/496245aa4365d0827390bd0b6fbd11287453b3a1
- https://github.com/advisories/GHSA-hjfx-8p6c-g7gx
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2021-94.yaml
- https://github.com/python-pillow/Pillow
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MQHA5HAIBOYI3R6HDWCLAGFTIQP767FL
- https://pillow.readthedocs.io/en/stable/releasenotes/8.2.0.html#cve-2021-28678-fix-blp-dos
- https://security.gentoo.org/glsa/202107-33
