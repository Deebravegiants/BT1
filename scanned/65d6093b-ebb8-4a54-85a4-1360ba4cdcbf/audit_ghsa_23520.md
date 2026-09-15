# [H] OpenDaylight Controller DoS

## Summary
Severity: High
Advisory: GHSA-8p5x-w9cv-92hv
CVE: CVE-2017-1000361
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8p5x-w9cv-92hv
Type: github-advisory

## Affected
- Maven: `org.opendaylight.controller:releasepom` — affected >=0

## Details
DOMRpcImplementationNotAvailableException when sending Port-Status packets to OpenDaylight. Controller launches exceptions and consumes more CPU resources. Component: OpenDaylight is vulnerable to this flaw. Version: The tested versions are OpenDaylight 3.3 and 4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000361
- https://aaltodoc.aalto.fi/bitstream/handle/123456789/21584/master_Bidaj_Andi_2016.pdf
