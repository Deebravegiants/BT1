# [M] Quadratic complexity in node ID cache clearing

## Summary
Severity: Medium
Advisory: BIT-libpython-2025-12084
Aliases: BIT-python-2025-12084, BIT-python-min-2025-12084, CVE-2025-12084, PSF-2025-16
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-libpython-2025-12084
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.2

## Details
When building nested elements using xml.dom.minidom methods such as appendChild() that have a dependency on _clear_id_cache() the algorithm is quadratic. Availability can be impacted when building excessively nested documents.

## References
- https://github.com/python/cpython/commit/027f21e417b26eed4505ac2db101a4352b7c51a0
- https://github.com/python/cpython/commit/08d8e18ad81cd45bc4a27d6da478b51ea49486e4
- https://github.com/python/cpython/commit/27648a1818749ef44c420afe6173af6868715437
- https://github.com/python/cpython/commit/41f468786762348960486c166833a218a0a436af
- https://github.com/python/cpython/commit/57937a8e5e293f0dcba5115f7b7a11b1e0c9a273
- https://github.com/python/cpython/commit/8d2d7bb2e754f8649a68ce4116271a4932f76907
- https://github.com/python/cpython/commit/9c9dda6625a2a90d2a06c657eee021d6be19842d
- https://github.com/python/cpython/commit/a46c10ec9d4050ab67b8a932e0859a2ea60c3cb8
- https://github.com/python/cpython/commit/a696ba8b4d42fd632afc9bc88ad830a2e4cceed8
- https://github.com/python/cpython/commit/c97e87593063d84a2bd9fe7068b30eb44de23dc0
- https://github.com/python/cpython/commit/ddcd2acd85d891a53e281c773b3093f9db953964
- https://github.com/python/cpython/commit/e91c11449cad34bac3ea55ee09ca557691d92b53
- https://github.com/python/cpython/issues/142145
- https://github.com/python/cpython/pull/142146
- https://nvd.nist.gov/vuln/detail/CVE-2025-12084
