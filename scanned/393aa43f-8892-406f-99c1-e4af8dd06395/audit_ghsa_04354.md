# [M] sanic-cors contains an improper regular expression in the try_match() function

## Summary
Severity: Medium
Advisory: GHSA-94jw-hqvj-vw74
CVE: CVE-2026-37737
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-94jw-hqvj-vw74
Type: github-advisory

## Affected
- PyPI: `sanic-cors` — affected >=0

## Details
sanic-cors version 2.2.0 and prior contains an improper regular expression in the try_match() function in sanic_cors/core.py that uses re.match without end-anchoring. This allows an attacker to bypass CORS origin allowlists by registering a domain that begins with a trusted origin string, to gain unauthorized access to cross-origin requests for authenticated resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-37737
- https://github.com/ashleysommer/sanic-cors
- https://github.com/ashleysommer/sanic-cors/blob/master/sanic_cors/core.py
- https://github.com/npbhatter17/security-advisories/blob/main/CVE-2026-37737-sanic-cors-advisory.md
- https://pypi.org/project/Sanic-Cors
