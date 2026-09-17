# [M] HTTP Request Smuggling in netius

## Summary
Severity: Medium
Advisory: GHSA-wm2m-xrrp-j74c
CVE: CVE-2020-7655
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-18
Source: https://github.com/advisories/GHSA-wm2m-xrrp-j74c
Type: github-advisory

## Affected
- PyPI: `netius` — affected >=0 <1.17.58

## Details
netius prior to 1.17.58 is vulnerable to HTTP Request Smuggling. HTTP pipelining issues and request smuggling attacks might be possible due to incorrect Transfer encoding header parsing which could allow for CL:TE or TE:TE attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7655
- https://github.com/hivesolutions/netius/commit/9830881ef68328f8ea9c7901db1d11690677e7d1
- https://github.com/advisories/GHSA-wm2m-xrrp-j74c
- https://github.com/hivesolutions/netius
- https://github.com/pypa/advisory-database/tree/main/vulns/netius/PYSEC-2020-242.yaml
- https://snyk.io/vuln/SNYK-PYTHON-NETIUS-569141
