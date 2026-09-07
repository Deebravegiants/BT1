# [H] Incorrect header handling in mod-wsgi

## Summary
Severity: High
Advisory: GHSA-7527-8855-9cf8
CVE: CVE-2022-2255
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-08-26
Source: https://github.com/advisories/GHSA-7527-8855-9cf8
Type: github-advisory

## Affected
- PyPI: `mod-wsgi` — affected >=0 <4.9.3

## Details
A vulnerability was found in mod_wsgi. The X-Client-IP header is not removed from a request from an untrusted proxy, allowing an attacker to pass the X-Client-IP header to the target WSGI application because the condition to remove it is missing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2255
- https://github.com/GrahamDumpleton/mod_wsgi/commit/af3c0c2736bc0b0b01fa0f0aad3c904b7fa9c751
- https://github.com/GrahamDumpleton/mod_wsgi
- https://github.com/GrahamDumpleton/mod_wsgi/blob/4.9.2/src/server/mod_wsgi.c#L13940-L13941
- https://github.com/GrahamDumpleton/mod_wsgi/blob/4.9.2/src/server/mod_wsgi.c#L14046-L14082
- https://github.com/pypa/advisory-database/tree/main/vulns/mod-wsgi/PYSEC-2022-254.yaml
- https://lists.debian.org/debian-lts-announce/2022/09/msg00021.html
- https://modwsgi.readthedocs.io/en/latest/release-notes/version-4.9.3.html
