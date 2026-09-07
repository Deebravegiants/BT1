# [H] Special Element Injection in notebook

## Summary
Severity: High
Advisory: GHSA-hwvq-6gjx-j797
CVE: CVE-2021-32798
CWE: CWE-75, CWE-79, CWE-80
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-23
Source: https://github.com/advisories/GHSA-hwvq-6gjx-j797
Type: github-advisory

## Affected
- PyPI: `notebook` — affected >=0 <5.7.11
- PyPI: `notebook` — affected >=6.0.0 <6.4.1

## Details
### Impact

Untrusted notebook can execute code on load. This is a remote code execution, but requires user action to open a notebook.

### Patches

5.7.11, 6.4.1

### References

[OWASP Page on Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html#injection-prevention-rules)

### For more information

If you have any questions or comments about this advisory, or vulnerabilities to report, please email our security list security@ipython.org.

Credit: Guillaume Jeanne from Google


### Example:

A notebook with the following content in a cell and it would display an alert when opened for the first time in Notebook (in an untrusted state):

```
{ "cell_type": "code", "execution_count": 0, "metadata": {}, "outputs": [ { "data": { "text/html": [ "<select><iframe></select><img src=x: onerror=alert('xss')>\n"], "text/plain": [] }, "metadata": {}, "output_type": "display_data" } ], "source": [ "" ] }
````

## References
- https://github.com/jupyter/notebook/security/advisories/GHSA-hwvq-6gjx-j797
- https://nvd.nist.gov/vuln/detail/CVE-2021-32798
- https://github.com/jupyter/notebook/commit/79fc76e890a8ec42f73a3d009e44ef84c14ef0d5
- https://github.com/jupyter/notebook
- https://github.com/pypa/advisory-database/tree/main/vulns/notebook/PYSEC-2021-118.yaml
