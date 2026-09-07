# [H] sniff_csv provides filesystem access even when enable_external_access is disabled in duckdb

## Summary
Severity: High
Advisory: GHSA-w2gf-jxc9-pf2q
CVE: CVE-2024-41672
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-w2gf-jxc9-pf2q
Type: github-advisory

## Affected
- PyPI: `duckdb` — affected >=1.0.0 <1.1.0

## Details
### Summary
Content in filesystem is accessible for reading using `sniff_csv`, even with `enable_external_access=false`. 

### Details
During a pentest, a security researcher was able to access environment variable data and other system data by using the `sniff_csv` function, even though we set `enable_external_access` to false. 

### PoC
```SQL
SET enable_external_access=false;
SET lock_configuration=true;

SELECT Columns FROM sniff_csv('/proc/self/environ');
```

### Impact
Provides an attacker with access to filesystem even when access is expected to be disabled and other similar functions do NOT provide access. 

For example `select * from read_csv('/proc/self/environ')` fails with a permission error. 

There seems to be two vectors to this vulnerability: 
1. Access to files that should otherwise not be allowed. (We expect `Permission Error: Scanning CSV files is disabled through configuration` and not to provide any access to the file or even acknowledge that it exists). 
2. The content from a (non-csv?) file can be read (e.g. `/etc/hosts`, `proc/self/environ`, etc) even though that doesn't seem to be the intent of the sniff_csv function (my understanding is it's intending to provide information about the shape of the data, but not provide the data itself). 

### Workaround
It is possible to work around the issue by disabling the local file system using the `disabled_filesystems` setting:
```SQL
SET disabled_filesystems='LocalFileSystem';
SET lock_configuration=true;

SELECT Columns FROM sniff_csv('/proc/self/environ');
```

will result in `Permission Error: File system LocalFileSystem has been disabled by configuration`.

### Fix
A fix has been merged into the `main` branch (https://github.com/duckdb/duckdb/pull/13133), and will be released with the next DuckDB release.

## References
- https://github.com/duckdb/duckdb/security/advisories/GHSA-w2gf-jxc9-pf2q
- https://nvd.nist.gov/vuln/detail/CVE-2024-41672
- https://github.com/duckdb/duckdb/pull/13133
- https://github.com/duckdb/duckdb/commit/c9b7c98aa0e1cd7363fe8bb8543a95f38e980d8a
- https://github.com/duckdb/duckdb
- https://github.com/pypa/advisory-database/tree/main/vulns/duckdb/PYSEC-2024-203.yaml
