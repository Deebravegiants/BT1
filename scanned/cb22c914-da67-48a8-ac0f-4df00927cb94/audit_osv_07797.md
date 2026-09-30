# [M] Domain restrictions bypass via DNS Rebinding in WireMock and WireMock Studio

## Summary
Severity: Medium
Advisory: BIT-wiremock-2023-41329
Aliases: CVE-2023-41329, GHSA-pmxq-pj47-j8j4, PYSEC-2026-2050
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-wiremock-2023-41329
Type: osv

## Affected
- Bitnami: `wiremock` — affected >=3.0.0 <3.0.3

## Details
WireMock is a tool for mocking HTTP services. The proxy mode of WireMock, can be protected by the network restrictions configuration, as documented in Preventing proxying to and recording from specific target addresses. These restrictions can be configured using the domain names, and in such a case the configuration is vulnerable to the DNS rebinding attacks. A similar patch was applied in WireMock 3.0.0 for the WireMock Webhook Extensions. The root cause of the attack is a defect in the logic which allows for a race condition triggered by a DNS server whose address expires in between the initial validation and the outbound network request that might go to a domain that was supposed to be prohibited. Control over a DNS service is required to exploit this attack, so it has high execution complexity and limited impact. This issue has been addressed in versions 2.35.1-1 and 3.0.3-1. Users are advised to upgrade. Users unable to upgrade should either configure firewall rules to define the list of permitted destinations or to configure WireMock to use IP addresses instead of the domain names.

## References
- https://github.com/wiremock/wiremock/security/advisories/GHSA-pmxq-pj47-j8j4
- https://nvd.nist.gov/vuln/detail/CVE-2023-41329
- https://wiremock.org/docs/configuration/#preventing-proxying-to-and-recording-from-specific-target-addresses
