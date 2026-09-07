# [M] DoS with algorithms that use PBKDF2 due to unbounded PBES2 Count value

## Summary
Severity: Medium
Advisory: GHSA-cw2r-4p82-qv79
CVE: CVE-2023-6681
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-12-28
Source: https://github.com/advisories/GHSA-cw2r-4p82-qv79
Type: github-advisory

## Affected
- PyPI: `jwcrypto` — affected >=0 <1.5.1

## Details
### Impact
Denial of Service,
Applications that allow the use of the PBKDF2 algorithm.

### Patches
A [patch](https://github.com/latchset/jwcrypto/commit/d2655d370586cb830e49acfb450f87598da60be8) is available that sets the maximum number of default rounds.

### Workarounds
Applications that do not need to use PBKDF2 should simply specify the algorithms use and exclude it from the list.
Applications that need to use the algorithm should upgrade to the new version that allows to set a maximum rounds number.

### Acknowledgement
The issues was reported by Jingcheng Yang and Jianjun Chen from Sichuan University
and Zhongguancun Lab

## References
- https://github.com/latchset/jwcrypto/security/advisories/GHSA-cw2r-4p82-qv79
- https://nvd.nist.gov/vuln/detail/CVE-2023-6681
- https://github.com/latchset/jwcrypto/commit/d2655d370586cb830e49acfb450f87598da60be8
- https://access.redhat.com/errata/RHSA-2024:3267
- https://access.redhat.com/errata/RHSA-2024:9281
- https://access.redhat.com/security/cve/CVE-2023-6681
- https://bugzilla.redhat.com/show_bug.cgi?id=2260843
- https://github.com/latchset/jwcrypto
- https://github.com/pypa/advisory-database/tree/main/vulns/jwcrypto/PYSEC-2024-104.yaml
