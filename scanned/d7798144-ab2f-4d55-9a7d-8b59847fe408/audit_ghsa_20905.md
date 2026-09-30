# [H] MEI2Volpiano is vulnerable to XML External Entity (XXE), leading to a Denial of Service (DoS)

## Summary
Severity: High
Advisory: GHSA-6xm7-3cc5-47f9
CVE: CVE-2022-37189
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-08
Source: https://github.com/advisories/GHSA-6xm7-3cc5-47f9
Type: github-advisory

## Affected
- PyPI: `mei2volpiano` — affected >=0

## Details
DDMAL MEI2Volpiano 0.8.2 is vulnerable to XML External Entity (XXE), leading to a Denial of Service. This occurs due to the usage of the unsafe 'xml.etree' library to parse untrusted XML input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37189
- https://docs.python.org/3/library/xml.html#xml-vulnerabilities
- https://github.com/DDMAL/MEI2Volpiano
- https://github.com/DDMAL/MEI2Volpiano/blob/987b70fff991235e682405f901388af0f414eaa8/mei2volpiano/mei2volpiano.py#L59
- https://pyup.io/vulnerabilities/CVE-2022-37189/50928
