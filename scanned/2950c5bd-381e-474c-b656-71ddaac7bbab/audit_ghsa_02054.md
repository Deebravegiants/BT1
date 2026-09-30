# [H] The Fuck Arbitrary File Deletion via Path Traversal

## Summary
Severity: High
Advisory: GHSA-8wwf-2644-f8x4
CVE: CVE-2021-34363
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-06-15
Source: https://github.com/advisories/GHSA-8wwf-2644-f8x4
Type: github-advisory

## Affected
- PyPI: `thefuck` — affected >=0 <3.31

## Details
The thefuck (aka _The Fuck_) is app that corrects errors in previous console commands. _The Fuck_ python package before 3.31 allows Path Traversal that leads to arbitrary file deletion via the `undo archive operation` feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34363
- https://github.com/nvbn/thefuck/commit/e343c577cd7da4d304b837d4a07ab4df1e023092
- https://github.com/nvbn/thefuck
- https://github.com/nvbn/thefuck/releases/tag/3.31
- https://github.com/pypa/advisory-database/tree/main/vulns/thefuck/PYSEC-2021-97.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4MEDDLBFVRUQHPYIBJ4MFM3M4NUJUXL5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YA6UNQSOY6M3NJDZLS6YJXTS4WGDMEEJ
- https://vuln.ryotak.me/advisories/48
