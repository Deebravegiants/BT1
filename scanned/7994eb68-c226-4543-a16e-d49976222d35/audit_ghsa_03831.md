# [H] python-engineio vulnerable to Cross-Site Request Forgery (CSRF) 

## Summary
Severity: High
Advisory: GHSA-j3jp-gvr5-7hwq
CVE: CVE-2019-13611
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-07-30
Source: https://github.com/advisories/GHSA-j3jp-gvr5-7hwq
Type: github-advisory

## Affected
- PyPI: `python-engineio` — affected >=0 <3.9.0

## Details
## WebSocket cross-origin vulnerability

### Impact
This is a Cross-Site Request Forgery (CSRF) vulnerability. It affects Socket.IO and Engine.IO web servers that authenticate clients using cookies.

### Patches
python-engineio version 3.9.0 patches this vulnerability by adding server-side Origin header checks.

### Workarounds
Do not use cookies for client authentication, or else add a CSRF token to the connection URL.

### References
https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)
https://www.christian-schneider.net/CrossSiteWebSocketHijacking.html

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [python-engineio](http://github.com/miguelgrinberg/python-engineio)

## References
- https://github.com/miguelgrinberg/python-engineio/security/advisories/GHSA-j3jp-gvr5-7hwq
- https://nvd.nist.gov/vuln/detail/CVE-2019-13611
- https://github.com/miguelgrinberg/python-engineio/issues/128
- https://github.com/advisories/GHSA-j3jp-gvr5-7hwq
- https://github.com/miguelgrinberg/python-engineio
- https://github.com/pypa/advisory-database/tree/main/vulns/python-engineio/PYSEC-2019-170.yaml
