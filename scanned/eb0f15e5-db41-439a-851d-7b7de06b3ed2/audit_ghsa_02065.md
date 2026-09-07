# [M] Reflected cross-site scripting issue in Datasette

## Summary
Severity: Medium
Advisory: GHSA-xw7c-jx9m-xh5g
CVE: CVE-2021-32670
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-07
Source: https://github.com/advisories/GHSA-xw7c-jx9m-xh5g
Type: github-advisory

## Affected
- PyPI: `datasette` — affected >=0 <0.56.1

## Details
### Impact

The `?_trace=1` debugging feature in Datasette does not correctly escape generated HTML, resulting in a [reflected cross-site scripting](https://owasp.org/www-community/attacks/xss/#reflected-xss-attacks) vulnerability.

This vulnerability is particularly relevant if your Datasette installation includes authenticated features using plugins such as [datasette-auth-passwords](https://datasette.io/plugins/datasette-auth-passwords) as an attacker could use the vulnerability to access protected data.

### Patches

Datasette 0.57 and 0.56.1 both include patches for this issue.

### Workarounds

If you run Datasette behind a proxy you can workaround this issue by rejecting any incoming requests with `?_trace=` or `&_trace=` in their query string parameters.

### References

- [OWASP guide to reflected cross-site scripting](https://owasp.org/www-community/attacks/xss/#reflected-xss-attacks)
- [Datasette issue #1360](https://github.com/simonw/datasette/issues/1360)

### For more information
If you have any questions or comments about this advisory:
* Open a discussion in [simonw/datasette](https://github.com/simonw/datasette/discussions)
* Email us at `swillison+datasette @ gmail.com`

## References
- https://github.com/simonw/datasette/security/advisories/GHSA-xw7c-jx9m-xh5g
- https://github.com/simonw/datasette/issues/1360
- https://datasette.io/plugins/datasette-auth-passwords
- https://github.com/advisories/GHSA-gff3-739c-gxfq
- https://github.com/pypa/advisory-database/tree/main/vulns/datasette/PYSEC-2021-89.yaml
- https://github.com/simonw/datasette
- https://owasp.org/www-community/attacks/xss/#reflected-xss-attacks
- https://pypi.org/project/datasette
