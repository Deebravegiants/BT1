# [H] CVE-2019-19275

## Summary
Severity: High
Advisory: CVE-2019-19275
Aliases: GHSA-7xxv-wpxj-mx5v, PYSEC-2019-131
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-19275
Type: osv

## Details
typed_ast 1.3.0 and 1.3.1 has an ast_for_arguments out-of-bounds read. An attacker with the ability to cause a Python interpreter to parse Python source (but not necessarily execute it) may be able to crash the interpreter process. This could be a concern, for example, in a web-based service that parses (but does not execute) Python code. (This issue also affected certain Python 3.8.0-alpha prereleases.)

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LG5H4Q6LFVRX7SFXLBEJMNQFI4T5SCEA/
- https://bugs.python.org/issue36495
- https://github.com/python/cpython/commit/a4d78362397fc3bced6ea80fbc7b5f4827aec55e
- https://github.com/python/cpython/commit/dcfcd146f8e6fc5c2fc16a4c192a0c5f5ca8c53c
- https://github.com/python/typed_ast/commit/156afcb26c198e162504a57caddfe0acd9ed7dce
- https://github.com/python/typed_ast/commit/dc317ac9cff859aa84eeabe03fb5004982545b3b
