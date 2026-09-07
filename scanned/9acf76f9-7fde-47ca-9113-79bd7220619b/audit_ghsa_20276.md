# [H] Command Injection in Nuitka

## Summary
Severity: High
Advisory: GHSA-4v3r-hqr9-69jf
CVE: CVE-2022-2054
CWE: CWE-77, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-13
Source: https://github.com/advisories/GHSA-4v3r-hqr9-69jf
Type: github-advisory

## Affected
- PyPI: `Nuitka` — affected >=0 <0.9

## Details
Nuitka 0.8.4 and prior is vulnerable to command injection. A patch is available and anticipated to be part of the `0.9` release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2054
- https://github.com/Nuitka/Nuitka/commit/1765ffce2a9ab859853210337390de242cd80712
- https://github.com/nuitka/nuitka/commit/09647745d7cbb6ff32f9fa948f19d5558b32bcad
- https://github.com/nuitka/nuitka
- https://github.com/pypa/advisory-database/tree/main/vulns/nuitka/PYSEC-2022-209.yaml
- https://huntr.dev/bounties/ea4a842c-c48c-4aae-a599-3305125c63a7
