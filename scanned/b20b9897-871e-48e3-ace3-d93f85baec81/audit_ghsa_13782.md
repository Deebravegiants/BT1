# [C] Ibis PyArrow dependency allows arbitrary code execution when loading a malicious data file

## Summary
Severity: Critical
Advisory: GHSA-x563-6hqv-26mr
CWE: CWE-502
Ecosystem: PyPI
Published: 2023-11-17
Source: https://github.com/advisories/GHSA-x563-6hqv-26mr
Type: github-advisory

## Affected
- PyPI: `ibis-framework` — affected >=0 <7.1.0

## Details
### Impact

Deserialization of untrusted data in IPC and Parquet readers in PyArrow versions 0.14.0 to 14.0.0 allows arbitrary code execution. An application is vulnerable if it reads Arrow IPC, Feather or Parquet data from untrusted sources (for example user-supplied input files). This vulnerability only affects PyArrow, not other Apache Arrow implementations or bindings.

Note that Ibis itself makes **extremely limited** use of `pyarrow.parquet.read_table`:

1. `read_table` is used in tests, where the input file is entirely controlled by the Ibis developers
2. `read_table` is used in the `ibis/examples/__init__.py` as a fallback for backends that don't support reading Parquet directly. Parquet data used in `ibis.examples` are also managed by the Ibis developers. This Parquet data is generated from CSV files and SQLite databases.
3. The Pandas and Dask backends both use PyArrow to read Parquet files and are therefore affected.

Ibis **does not** make use of APIs that directly read from either Arrow IPC files or Feather files.

### Patches

Ibis imports the `pyarrow_hotfix` package wherever pyarrow is used, as of version 7.1.0.

Upgrading to Arrow 14.0.1 is also a possible solution, starting in Ibis 7.1.0.

### Workarounds

Install [`pyarrow_hotfix`](https://pypi.org/project/pyarrow-hotfix/) and run `import pyarrow_hotfix` ahead of any and all `import ibis` statements.

For example:

```python
import ibis
```

becomes

```python
import pyarrow_hotfix
import ibis
```

### References

https://www.cve.org/CVERecord?id=CVE-2023-47248
https://nvd.nist.gov/vuln/detail/CVE-2023-47248

## References
- https://github.com/ibis-project/ibis/security/advisories/GHSA-x563-6hqv-26mr
- https://github.com/ibis-project/ibis/commit/0fa1e5dc06783c01e912e8de4d7e10186ca0e364
- https://github.com/ibis-project/ibis
- https://github.com/ibis-project/ibis/releases/tag/7.1.0
