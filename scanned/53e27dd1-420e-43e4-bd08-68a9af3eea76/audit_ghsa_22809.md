# [H] bsdiff4 out-of-bounds write via patch file

## Summary
Severity: High
Advisory: GHSA-f8m3-jpxr-hm5x
CVE: CVE-2020-15904
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f8m3-jpxr-hm5x
Type: github-advisory

## Affected
- PyPI: `bsdiff4` — affected >=0 <1.2.0

## Details
A buffer overflow in the patching routine of bsdiff4 before 1.2.0 allows an attacker to write to heap memory (beyond allocated bounds) via a crafted patch file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15904
- https://github.com/ilanschnell/bsdiff4/commit/49a4cee2feef7deaf9d89e5e793a8824930284d7
- https://github.com/ilanschnell/bsdiff4
- https://github.com/ilanschnell/bsdiff4/blob/9a84c2ee01f5ba0742d18c9f3b3d5244ae7fb302/CHANGELOG.txt#L30-L31
- https://github.com/ilanschnell/bsdiff4/blob/master/CHANGELOG.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/bsdiff4/PYSEC-2020-30.yaml
