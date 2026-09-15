# [H] CoAPthon DoS due to Exceptions

## Summary
Severity: High
Advisory: GHSA-5xc6-fpc7-4qvg
CVE: CVE-2018-12680
CWE: CWE-400, CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-04-08
Source: https://github.com/advisories/GHSA-5xc6-fpc7-4qvg
Type: github-advisory

## Affected
- PyPI: `CoAPthon` — affected >=0

## Details
The `Serialize.deserialize()` method in CoAPthon 3.1, 4.0.0, 4.0.1, and 4.0.2 mishandles certain exceptions, leading to a denial of service in applications that use this library (e.g., the standard CoAP server, CoAP client, CoAP reverse proxy, example collect CoAP server and client) when they receive crafted CoAP messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12680
- https://github.com/Tanganelli/CoAPthon/issues/135
- https://github.com/Tanganelli/CoAPthon
- https://github.com/advisories/GHSA-5xc6-fpc7-4qvg
- https://github.com/pypa/advisory-database/tree/main/vulns/coapthon/PYSEC-2019-165.yaml
