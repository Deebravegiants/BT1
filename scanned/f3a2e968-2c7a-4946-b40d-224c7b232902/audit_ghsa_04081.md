# [H] CoAPthon3 vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-c6fm-rgw4-8q73
CVE: CVE-2018-12679
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-04-08
Source: https://github.com/advisories/GHSA-c6fm-rgw4-8q73
Type: github-advisory

## Affected
- PyPI: `CoAPthon3` — affected >=0

## Details
The Serialize.deserialize() method in CoAPthon3 1.0 and 1.0.1 mishandles certain exceptions, leading to a denial of service in applications that use this library (e.g., the standard CoAP server, CoAP client, example collect CoAP server and client) when they receive crafted CoAP messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12679
- https://github.com/Tanganelli/CoAPthon3/issues/16
- https://github.com/Tanganelli/CoAPthon3
- https://github.com/advisories/GHSA-c6fm-rgw4-8q73
- https://github.com/pypa/advisory-database/tree/main/vulns/coapthon3/PYSEC-2019-166.yaml
