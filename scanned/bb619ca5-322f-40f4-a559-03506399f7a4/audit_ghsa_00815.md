# [M] CSRF tokens leaked in URL by canned query form

## Summary
Severity: Medium
Advisory: GHSA-q6j3-c4wc-63vw
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-08-11
Source: https://github.com/advisories/GHSA-q6j3-c4wc-63vw
Type: github-advisory

## Affected
- PyPI: `datasette` — affected >=0 <0.46

## Details
### Impact

The HTML form for a read-only canned query includes the hidden CSRF token field added in #798 for writable canned queries (#698).

This means that submitting those read-only forms exposes the CSRF token in the URL - for example on https://latest.datasette.io/fixtures/neighborhood_search submitting the form took me to:

https://latest.datasette.io/fixtures/neighborhood_search?text=down&csrftoken=CSRFTOKEN-HERE

This token could potentially leak to an attacker if the resulting page has a link to an external site on it and the user clicks the link, since the token would be exposed in the referral logs.

### Patches

A fix for this issue has been released in Datasette 0.46.

### Workarounds

You can fix this issue in a Datasette instance without upgrading by copying the [0.46 query.html template](https://raw.githubusercontent.com/simonw/datasette/0.46/datasette/templates/query.html) into a custom `templates/` directory and running Datasette with the `--template-dir=templates/` option.

### References

Issue 918 discusses this in details: https://github.com/simonw/datasette/issues/918

### For more information

Contact swillison at gmail with any questions.

## References
- https://github.com/simonw/datasette/security/advisories/GHSA-q6j3-c4wc-63vw
- https://github.com/simonw/datasette/issues/918
- https://github.com/simonw/datasette/commit/7f10f0f7664d474c1be82bf668829e3b736a3d2b
- https://github.com/simonw/datasette
- https://snyk.io/vuln/SNYK-PYTHON-DATASETTE-598229
