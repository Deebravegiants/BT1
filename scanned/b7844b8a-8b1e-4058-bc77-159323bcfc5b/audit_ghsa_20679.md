# [H] Uncontrolled Resource Consumption in asyncua and opcua

## Summary
Severity: High
Advisory: GHSA-mfpj-3qhm-976m
CVE: CVE-2022-25304
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-24
Source: https://github.com/advisories/GHSA-mfpj-3qhm-976m
Type: github-advisory

## Affected
- PyPI: `asyncua` — affected >=0 <0.9.96
- PyPI: `opcua` — affected >=0

## Details
All versions of package opcua; all versions of package asyncua are vulnerable to Denial of Service (DoS) due to a missing limitation on the number of received chunks - per single session or in total for all concurrent sessions. An attacker can exploit this vulnerability by sending an unlimited number of huge chunks (e.g. 2GB each) without sending the Final closing chunk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25304
- https://github.com/FreeOpcUa/python-opcua/issues/1466
- https://github.com/FreeOpcUa/opcua-asyncio/commit/01c7acf047887b62d979cd4373d370e72a4b9057
- https://github.com/FreeOpcUa/opcua-asyncio
- https://security.snyk.io/vuln/SNYK-PYTHON-ASYNCUA-2988731
- https://security.snyk.io/vuln/SNYK-PYTHON-OPCUA-2988730
