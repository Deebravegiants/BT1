# [H] CVE-2024-34402

## Summary
Severity: High
Advisory: CVE-2024-34402
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2024-34402
Type: osv

## Details
An issue was discovered in uriparser through 0.9.7. ComposeQueryEngine in UriQuery.c has an integer overflow via long keys or values, with a resultant buffer overflow.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5R36L762D3KX3GA66OOPWW7M7KKDRXDP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CZ6KEUQXWCTYXGTBMZDD7CHJCYI52XY3/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34402.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5R36L762D3KX3GA66OOPWW7M7KKDRXDP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CZ6KEUQXWCTYXGTBMZDD7CHJCYI52XY3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UG4J7PD475LSCGCSHFU4GMU4TWLDSNW2/
- https://nvd.nist.gov/vuln/detail/CVE-2024-34402
- https://github.com/uriparser/uriparser/issues/183
- https://github.com/uriparser/uriparser/pull/185
- http://www.openwall.com/lists/oss-security/2024/05/06/1
- http://www.openwall.com/lists/oss-security/2024/05/06/3
