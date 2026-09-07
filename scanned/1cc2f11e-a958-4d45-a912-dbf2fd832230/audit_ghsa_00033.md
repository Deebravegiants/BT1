# [H] PyKMIP Denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-gfv6-cj92-g3hx
CVE: CVE-2018-1000872
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-gfv6-cj92-g3hx
Type: github-advisory

## Affected
- PyPI: `pykmip` — affected >=0 <0.8.0

## Details
OpenKMIP PyKMIP version All versions before 0.8.0 contains a CWE 399: Resource Management Errors (similar issue to CVE-2015-5262) vulnerability in PyKMIP server that can result in DOS: the server can be made unavailable by one or more clients opening all of the available sockets. This attack appear to be exploitable via A client or clients open sockets with the server and then never close them. This vulnerability appears to have been fixed in 0.8.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000872
- https://github.com/OpenKMIP/PyKMIP/issues/430
- https://github.com/OpenKMIP/PyKMIP/commit/3a7b880bdf70d295ed8af3a5880bab65fa6b3932
- https://github.com/OpenKMIP/PyKMIP
- https://github.com/advisories/GHSA-gfv6-cj92-g3hx
- https://github.com/pypa/advisory-database/tree/main/vulns/pykmip/PYSEC-2018-22.yaml
