# [H] PyGreSQL Might Be Vulnerable to Encoding-Based SQL Injection

## Summary
Severity: High
Advisory: GHSA-xv6x-43gq-4hfj
CVE: CVE-2009-2940
CWE: CWE-89
Ecosystem: PyPI
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-xv6x-43gq-4hfj
Type: github-advisory

## Affected
- PyPI: `PyGreSQL` — affected >=0
- PyPI: `PyGreSQL` — affected >=4.0 <4.1

## Details
PyGreSQL 3.8 did not use PostgreSQL’s safe `string` and `bytea` functions in its own escaping functions. As a result, applications written to use PyGreSQL’s escaping functions are vulnerable to SQL injections when processing certain multi-byte character sequences. Because the safe functions require a database connection, to maintain backwards compatibility, `pg.escape_string()` and `pg.escape_bytea()` are still available, but applications will have to be adjusted to use the new `pyobj.escape_string()` and `pyobj.escape_bytea()` functions. For example, code containing:

```python
import pg
connection = pg.connect(...)
escaped = pg.escape_string(untrusted_input)
```
should be adjusted to use:

```python
import pg
connection = pg.connect(...)
escaped = connection.escape_string(untrusted_input)
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-2940
- https://github.com/PyGreSQL/PyGreSQL/commit/8e19320b130946eed6f043297e3e4e005a523612
- https://github.com/PyGreSQL/PyGreSQL/commit/f7237d773e6f4d5a7da3d99bb6bc5062bd07935e
- https://github.com/PyGreSQL/PyGreSQL
- https://github.com/pypa/advisory-database/tree/main/vulns/pygresql/PYSEC-2009-18.yaml
- http://ubuntu.com/usn/usn-870-1
- http://www.debian.org/security/2009/dsa-1911
