# [H] Integer overflow in pywin32

## Summary
Severity: High
Advisory: GHSA-hwfp-hg2m-9vr2
CVE: CVE-2021-32559
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-hwfp-hg2m-9vr2
Type: github-advisory

## Affected
- PyPI: `pywin32` — affected >=0 <301

## Details
An integer overflow exists in pywin32 prior to version b301 when adding an access control entry (ACE) to an access control list (ACL) that would cause the size to be greater than 65535 bytes. An attacker who successfully exploited this vulnerability could crash the vulnerable process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32559
- https://github.com/mhammond/pywin32/issues/1700
- https://github.com/mhammond/pywin32/pull/1701
- https://github.com/advisories/GHSA-hwfp-hg2m-9vr2
- https://github.com/fireeye/Vulnerability-Disclosures/blob/master/FEYE-2021-0017/FEYE-2021-0017.md
- https://github.com/mhammond/pywin32
- https://github.com/mhammond/pywin32/releases
- https://github.com/pypa/advisory-database/tree/main/vulns/pywin32/PYSEC-2021-112.yaml
