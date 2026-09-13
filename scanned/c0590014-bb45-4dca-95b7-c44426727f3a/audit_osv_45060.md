# [M] PYSEC-2024-188

## Summary
Severity: Medium
Advisory: PYSEC-2024-188
Aliases: CVE-2024-42353, GHSA-mg3v-6m49-jhp3
Ecosystem: PyPI
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-08-14
Source: https://osv.dev/vulnerability/PYSEC-2024-188
Type: osv

## Affected
- PyPI: `webob` — affected >=0 <f689bcf4f0a1f64f1735b1d5069aef5be6974b5b, >=0 <1.8.8

## Details
WebOb provides objects for HTTP requests and responses. When WebOb normalizes the HTTP Location header to include the request hostname, it does so by parsing the URL that the user is to be redirected to with Python's urlparse, and joining it to the base URL. `urlparse` however treats a `//` at the start of a string as a URI without a scheme, and then treats the next part as the hostname. `urljoin` will then use that hostname from the second part as the hostname replacing the original one from the request. This vulnerability is patched in WebOb version 1.8.8.

## References
- https://github.com/Pylons/webob/security/advisories/GHSA-mg3v-6m49-jhp3
- https://github.com/Pylons/webob/commit/f689bcf4f0a1f64f1735b1d5069aef5be6974b5b
