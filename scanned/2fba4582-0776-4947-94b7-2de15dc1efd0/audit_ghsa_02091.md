# [H] Potential infinite loop in Pillow

## Summary
Severity: High
Advisory: GHSA-7r7m-5h27-29hp
CVE: CVE-2021-28676
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-7r7m-5h27-29hp
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <8.2.0

## Details
An issue was discovered in Pillow before 8.2.0. For FLI data, FliDecode did not properly check that the block advance was non-zero, potentially leading to an infinite loop on load.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28676
- https://github.com/python-pillow/Pillow/pull/5377
- https://github.com/python-pillow/Pillow/commit/bb6c11fb889e6c11b0ee122b828132ee763b5856
- https://github.com/advisories/GHSA-7r7m-5h27-29hp
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2021-92.yaml
- https://github.com/python-pillow/Pillow
- https://lists.debian.org/debian-lts-announce/2021/07/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MQHA5HAIBOYI3R6HDWCLAGFTIQP767FL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MQHA5HAIBOYI3R6HDWCLAGFTIQP767FL
- https://pillow.readthedocs.io/en/stable/releasenotes/8.2.0.html#cve-2021-28676-fix-fli-dos
- https://security.gentoo.org/glsa/202107-33
