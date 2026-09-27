# [H] StripComments filter contains a regular expression that is vulnerable to ReDOS (Regular Expression Denial of Service)

## Summary
Severity: High
Advisory: GHSA-p5w8-wqhj-9hhf
CVE: CVE-2021-32839
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-10
Source: https://github.com/advisories/GHSA-p5w8-wqhj-9hhf
Type: github-advisory

## Affected
- PyPI: `sqlparse` — affected >=0.4.0 <0.4.2

## Details
### Impact
The formatter function that strips comments from a SQL contains a regular expression that is vulnerable to [ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) (Regular Expression Denial of Service). The regular expression may cause exponential backtracking on strings containing many repetitions of '\r\n' in SQL comments.

### Patches
The issues has been fixed in sqlparse 0.4.2.

### Workarounds
Only the formatting feature that removes comments from SQL statements is affected by this regular expression. As a workaround don't use the `sqlformat.format` function with keyword `strip_comments=True` or the `--strip-comments` command line flag when using the `sqlformat` command line tool.

### References
This issue was discovered by GitHub team members @erik-krogh and @yoff. It was found using a [CodeQL](https://codeql.github.com/) query which identifies inefficient regular expressions. You can see the results of the query on python-sqlparse by following [this link](https://lgtm.com/query/2223658096471222354/). 

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [sqlparse issue tracker](https://github.com/andialbrecht/sqlparse/issues)
* Email us at [albrecht.andi@gmail.com](mailto:albrecht.andi@gmail.com)

## References
- https://github.com/andialbrecht/sqlparse/security/advisories/GHSA-p5w8-wqhj-9hhf
- https://nvd.nist.gov/vuln/detail/CVE-2021-32839
- https://github.com/andialbrecht/sqlparse/commit/8238a9e450ed1524e40cb3a8b0b3c00606903aeb
- https://github.com/andialbrecht/sqlparse
- https://github.com/pypa/advisory-database/tree/main/vulns/sqlparse/PYSEC-2021-333.yaml
- https://lists.debian.org/debian-lts-announce/2024/12/msg00022.html
- https://securitylab.github.com/advisories/GHSL-2021-107-andialbrecht-sqlparse
