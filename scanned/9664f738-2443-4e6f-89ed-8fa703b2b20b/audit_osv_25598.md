# [H] FreeSWITCH allows remote users to trigger out of bounds write by offering an ICE candidate with unknown component ID

## Summary
Severity: High
Advisory: CVE-2023-40018
Aliases: GHSA-7mwp-86fv-hcg3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-15
Source: https://osv.dev/vulnerability/CVE-2023-40018
Type: osv

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.10.10, FreeSWITCH allows remote users to trigger out of bounds write by offering an ICE candidate with unknown component ID. When an SDP is offered with any ICE candidates with an unknown component ID, FreeSWITCH will make an out of bounds write to its  arrays. By abusing this vulnerability, an attacker is able to corrupt FreeSWITCH memory leading to an undefined behavior of the system or a crash of it. Version 1.10.10 contains a patch for this issue.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.10.10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40018.json
- https://github.com/signalwire/freeswitch/security/advisories/GHSA-7mwp-86fv-hcg3
- https://nvd.nist.gov/vuln/detail/CVE-2023-40018
