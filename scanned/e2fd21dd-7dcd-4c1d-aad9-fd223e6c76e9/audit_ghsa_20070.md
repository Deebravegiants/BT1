# [M] pyRdfa3 Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-894q-wpg5-mf2h
CVE: CVE-2022-4396
CWE: CWE-707, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-10
Source: https://github.com/advisories/GHSA-894q-wpg5-mf2h
Type: github-advisory

## Affected
- PyPI: `pyRdfa3` — affected >=0 <3.6.2

## Details
A vulnerability was found in RDFlib pyrdfa3 and classified as problematic. This issue affects the function `_get_option` of the file `pyRdfa/__init__.py`. The manipulation leads to cross site scripting. The attack may be initiated remotely. The name of the patch is ffd1d62dd50d5f4190013b39cedcdfbd81f3ce3e. It is recommended to apply a patch to fix this issue. The identifier VDB-215249 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4396
- https://github.com/RDFLib/pyrdfa3/issues/38
- https://github.com/RDFLib/pyrdfa3/pull/40
- https://github.com/RDFLib/pyrdfa3/commit/ffd1d62dd50d5f4190013b39cedcdfbd81f3ce3e
- https://github.com/RDFLib/pyrdfa3
- https://vuldb.com/?id.215249
