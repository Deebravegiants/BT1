# [H] Apache HTTP Server via mod_proxy_uwsgi HTTP response smuggling

## Summary
Severity: High
Advisory: GHSA-vcph-37mh-fqrh
CVE: CVE-2023-27522
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-vcph-37mh-fqrh
Type: github-advisory

## Affected
- PyPI: `uWSGI` — affected >=0 <2.0.22

## Details
HTTP Response Smuggling vulnerability in Apache HTTP Server via mod_proxy_uwsgi. This issue affects Apache HTTP Server from 2.4.30 through 2.4.55 and the uWSGI PyPI package prior to version 2.0.22. Special characters in the origin response header can truncate/split the response forwarded to the client.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27522
- https://github.com/apache/httpd/commit/d753ea76b5972a85349b68c31b59d04c60014f2d
- https://github.com/unbit/uwsgi/commit/58ee1df31fa9e9af106aaeabb82374c36b433822
- https://github.com/unbit/uwsgi/commit/acb03530aaaeaa810f28a5b64da619525940f569
- https://github.com/unbit/uwsgi
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00028.html
- https://security.gentoo.org/glsa/202309-01
- https://uwsgi-docs.readthedocs.io/en/latest/Changelog-2.0.22.html
