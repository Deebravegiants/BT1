# [H] dbt uses a SQLparse version with a high vulnerability

## Summary
Severity: High
Advisory: GHSA-p72q-h37j-3hq7
CWE: CWE-673
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-22
Source: https://github.com/advisories/GHSA-p72q-h37j-3hq7
Type: github-advisory

## Affected
- PyPI: `dbt-core` — affected >=1.6.0 <1.6.13
- PyPI: `dbt-core` — affected >=1.7.0 <1.7.13

## Details
### Summary

Using a version of `sqlparse` that has a security vulnerability and no way to update in current version of dbt core. Snyk recommends using `sqlparse==0.5` but this causes a conflict with dbt. Snyk states the issues is a recursion error: `SNYK-PYTHON-SQLPARSE-6615674`.

### Details
Dependency conflict error message:
```sh
The conflict is caused by:
    The user requested sqlparse==0.5
    dbt-core 1.7.10 depends on sqlparse<0.5 and >=0.2.3
```
Resolution was to pin `sqlparse >=0.5.0, <0.6.0` in `dbt-core`, patched in 1.6.13 and 1.7.13.

### PoC
From Snyk:

```python
import sqlparse
sqlparse.parse('[' * 10000 + ']' * 10000)
```

### Impact
Snyk classifies it as high 7.5/10.

### Patches
The bug has been fixed in [dbt-core v1.6.13](https://github.com/dbt-labs/dbt-core/releases/tag/v1.6.13) and [dbt-core v1.7.13](https://github.com/dbt-labs/dbt-core/releases/tag/v1.7.13).

### Mitigations
Bump `dbt-core` 1.6 and 1.7 dependencies to 1.6.13 and 1.7.13 respectively

## References
- https://github.com/andialbrecht/sqlparse/security/advisories/GHSA-2m57-hf25-phgg
- https://github.com/dbt-labs/dbt-core/security/advisories/GHSA-p72q-h37j-3hq7
- https://github.com/dbt-labs/dbt-core
- https://security.snyk.io/vuln/SNYK-PYTHON-SQLPARSE-6615674
