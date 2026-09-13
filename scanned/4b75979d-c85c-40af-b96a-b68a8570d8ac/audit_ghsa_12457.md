# [M] Improper Input Validation in mindsdb

## Summary
Severity: Medium
Advisory: GHSA-crhp-7c74-cg4c
CVE: CVE-2023-49796
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-12-12
Source: https://github.com/advisories/GHSA-crhp-7c74-cg4c
Type: github-advisory

## Affected
- PyPI: `mindsdb` — affected >=0 <23.11.4.1

## Details
### Impact

The put method in `mindsdb/mindsdb/api/http/namespaces/file.py` does not validate the user-controlled `name` value, which is used in a temporary file name, which is afterwards opened for writing on lines 122-125, which leads to path injection. This issue may lead to arbitrary file write. This vulnerability allows for writing files anywhere on the server that the filesystem permissions that the running server has access to.

### Patches

Use mindsdb staging branch or v23.11.4.1


### References

* GHSL-2023-184 
* See [CodeQL path injection prevention guidelines](https://codeql.github.com/codeql-query-help/python/py-path-injection/) and [OWASP guidelines](https://owasp.org/www-community/attacks/Path_Traversal).

## References
- https://github.com/mindsdb/mindsdb/security/advisories/GHSA-crhp-7c74-cg4c
- https://nvd.nist.gov/vuln/detail/CVE-2023-49796
- https://github.com/mindsdb/mindsdb/commit/8d13c9c28ebcf3b36509eb679378004d4648d8fe
- https://github.com/mindsdb/mindsdb
- https://github.com/mindsdb/mindsdb/blob/1821da719f34c022890c9ff25810218e71c5abbc/mindsdb/api/http/namespaces/file.py#L122-L125
- https://github.com/pypa/advisory-database/tree/main/vulns/mindsdb/PYSEC-2023-278.yaml
