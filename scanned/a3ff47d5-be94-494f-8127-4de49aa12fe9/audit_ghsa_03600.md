# [H] typed-ast Out-of-bounds Read

## Summary
Severity: High
Advisory: GHSA-m3jw-62m7-jjcm
CVE: CVE-2019-19274
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-m3jw-62m7-jjcm
Type: github-advisory

## Affected
- PyPI: `typed-ast` — affected >=1.3.0 <1.3.2

## Details
typed_ast 1.3.0 and 1.3.1 has a handle_keywordonly_args out-of-bounds read. An attacker with the ability to cause a Python interpreter to parse Python source (but not necessarily execute it) may be able to crash the interpreter process. This could be a concern, for example, in a web-based service that parses (but does not execute) Python code. (This issue also affected certain Python 3.8.0-alpha prereleases.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19274
- https://github.com/python/cpython/commit/a4d78362397fc3bced6ea80fbc7b5f4827aec55e
- https://github.com/python/cpython/commit/dcfcd146f8e6fc5c2fc16a4c192a0c5f5ca8c53c
- https://github.com/python/typed_ast/commit/156afcb26c198e162504a57caddfe0acd9ed7dce
- https://github.com/python/typed_ast/commit/dc317ac9cff859aa84eeabe03fb5004982545b3b
- https://bugs.python.org/issue36495
- https://github.com/advisories/GHSA-m3jw-62m7-jjcm
- https://github.com/pypa/advisory-database/tree/main/vulns/typed-ast/PYSEC-2019-130.yaml
- https://github.com/python/typed_ast
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LG5H4Q6LFVRX7SFXLBEJMNQFI4T5SCEA
