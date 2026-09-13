# [M] Server-Side Request Forgery in mindsdb

## Summary
Severity: Medium
Advisory: GHSA-34mr-6q8x-g9r6
CVE: CVE-2023-49795
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-12
Source: https://github.com/advisories/GHSA-34mr-6q8x-g9r6
Type: github-advisory

## Affected
- PyPI: `mindsdb` — affected >=0 <23.11.4.1

## Details
### Impact

The put method in `mindsdb/mindsdb/api/http/namespaces/file.py` does not validate the user-controlled URL in the source variable and uses it to create arbitrary requests on line 115, which allows Server-side request forgery (SSRF). This issue may lead to Information Disclosure. The SSRF allows for forging arbitrary network requests from the MindsDB server. It can be used to scan nodes in internal networks for open ports that may not be accessible externally, as well as scan for existing files on the internal network. It allows for retrieving files with csv, xls, xlsx, json or parquet extensions, which will be viewable via MindsDB GUI. For any other existing files, it is a blind SSRF.
 
### Patches

Use mindsdb staging branch or v23.11.4.1

### References

* GHSL-2023-182
[SSRF prevention cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).

## References
- https://github.com/mindsdb/mindsdb/security/advisories/GHSA-34mr-6q8x-g9r6
- https://nvd.nist.gov/vuln/detail/CVE-2023-49795
- https://github.com/mindsdb/mindsdb/commit/8d13c9c28ebcf3b36509eb679378004d4648d8fe
- https://github.com/mindsdb/mindsdb
- https://github.com/pypa/advisory-database/tree/main/vulns/mindsdb/PYSEC-2023-277.yaml
