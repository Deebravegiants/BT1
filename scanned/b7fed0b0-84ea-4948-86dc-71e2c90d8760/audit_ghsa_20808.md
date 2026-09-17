# [H] LIEF vulnerable to heap based buffer overflow via print_binary function

## Summary
Severity: High
Advisory: GHSA-42vg-2q93-fj6j
CVE: CVE-2022-38495
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-14
Source: https://github.com/advisories/GHSA-42vg-2q93-fj6j
Type: github-advisory

## Affected
- PyPI: `lief` — affected >=0

## Details
LIEF commit 365a16a was discovered to contain a heap-buffer overflow via the function `print_binary` at `/c/macho_reader.c`. Commit 0033b6312fd311b2e45e379c04a83d77c1e58578 contains a patch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38495
- https://github.com/lief-project/LIEF/issues/767
- https://github.com/lief-project/LIEF/commit/0033b6312fd311b2e45e379c04a83d77c1e58578
- https://github.com/lief-project/LIEF
- https://github.com/pypa/advisory-database/tree/main/vulns/lief/PYSEC-2022-276.yaml
