# [M] Capstone SEGV caused by a read memory access

## Summary
Severity: Medium
Advisory: GHSA-xx4j-rvcc-2vhr
CVE: CVE-2016-7151
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xx4j-rvcc-2vhr
Type: github-advisory

## Affected
- PyPI: `capstone` — affected >=0 <4.0.0

## Details
Capstone 3.0.4 has an out-of-bounds vulnerability (SEGV caused by a read memory access) in X86_insn_reg_intel in arch/X86/X86Mapping.c.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7151
- https://github.com/aquynh/capstone/pull/725
- https://github.com/aquynh/capstone/commit/87a25bb543c8e4c09b48d4b4a6c7db31ce58df06
- https://github.com/capstone-engine/capstone
- https://github.com/pypa/advisory-database/tree/main/vulns/capstone/PYSEC-2019-242.yaml
