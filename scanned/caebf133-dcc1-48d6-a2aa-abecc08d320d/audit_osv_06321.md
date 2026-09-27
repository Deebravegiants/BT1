# [H] Virtual environment (venv) activation scripts don't quote paths

## Summary
Severity: High
Advisory: BIT-libpython-2024-9287
Aliases: BIT-python-2024-9287, BIT-python-min-2024-9287, CVE-2024-9287, PSF-2024-12
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2024-9287
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.13.0 <3.13.1

## Details
A vulnerability has been found in the CPython `venv` module and CLI where path names provided when creating a virtual environment were not quoted properly, allowing the creator to inject commands into virtual environment "activation" scripts (ie "source venv/bin/activate"). This means that attacker-controlled virtual environments are able to run commands when the virtual environment is activated. Virtual environments which are not created by an attacker or which aren't activated before being used (ie "./venv/bin/python") are not affected.

## References
- https://github.com/python/cpython/commit/633555735a023d3e4d92ba31da35b1205f9ecbd7
- https://github.com/python/cpython/commit/8450b2482586857d689b6658f08de9c8179af7db
- https://github.com/python/cpython/commit/9286ab3a107ea41bd3f3c3682ce2512692bdded8
- https://github.com/python/cpython/commit/ae961ae94bf19c8f8c7fbea3d1c25cc55ce8ae97
- https://github.com/python/cpython/commit/d48cc82ed25e26b02eb97c6263d95dcaa1e9111b
- https://github.com/python/cpython/commit/e52095a0c1005a87eed2276af7a1f2f66e2b6483
- https://github.com/python/cpython/issues/124651
- https://github.com/python/cpython/pull/124712
- https://mail.python.org/archives/list/security-announce@python.org/thread/RSPJ2B5JL22FG3TKUJ7D7DQ4N5JRRBZL/
- https://nvd.nist.gov/vuln/detail/CVE-2024-9287
- https://security.netapp.com/advisory/ntap-20250425-0006/
- https://lists.debian.org/debian-lts-announce/2024/11/msg00024.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
