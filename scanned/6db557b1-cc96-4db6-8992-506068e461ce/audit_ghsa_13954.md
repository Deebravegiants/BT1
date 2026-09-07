# [H] High resource usage when parsing multipart form data with many fields

## Summary
Severity: High
Advisory: GHSA-xg9f-g7g7-2323
CVE: CVE-2023-25577
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-xg9f-g7g7-2323
Type: github-advisory

## Affected
- PyPI: `Werkzeug` — affected >=0 <2.2.3

## Details
Werkzeug's multipart form data parser will parse an unlimited number of parts, including file parts. Parts can be a small amount of bytes, but each requires CPU time to parse and may use more memory as Python data. If a request can be made to an endpoint that accesses `request.data`, `request.form`, `request.files`, or `request.get_data(parse_form_data=False)`, it can cause unexpectedly high resource usage.

This allows an attacker to cause a denial of service by sending crafted multipart data to an endpoint that will parse it. The amount of CPU time required can block worker processes from handling legitimate requests. The amount of RAM required can trigger an out of memory kill of the process. Unlimited file parts can use up memory and file handles. If many concurrent requests are sent continuously, this can exhaust or kill all available workers.

## References
- https://github.com/pallets/werkzeug/security/advisories/GHSA-xg9f-g7g7-2323
- https://nvd.nist.gov/vuln/detail/CVE-2023-25577
- https://github.com/pallets/werkzeug/commit/517cac5a804e8c4dc4ed038bb20dacd038e7a9f1
- https://github.com/pallets/werkzeug
- https://github.com/pallets/werkzeug/releases/tag/2.2.3
- https://github.com/pypa/advisory-database/tree/main/vulns/werkzeug/PYSEC-2023-58.yaml
- https://security.netapp.com/advisory/ntap-20230818-0003
- https://www.debian.org/security/2023/dsa-5470
