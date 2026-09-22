# [H] OpenFlow plugin for OpenDaylight LLDP Relay

## Summary
Severity: High
Advisory: GHSA-f2x4-547g-rp95
CVE: CVE-2015-1612
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-f2x4-547g-rp95
Type: github-advisory

## Affected
- Maven: `org.opendaylight.openflowplugin:openflowplugin` — affected >=0 <0.0.6-Helium-SR3

## Details
OpenFlow plugin for OpenDaylight before Helium SR3 allows remote attackers to spoof the SDN topology and affect the flow of data, related to the reuse of LLDP packets, aka "LLDP Relay."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1612
- https://git.opendaylight.org/gerrit/#/c/16193
- https://git.opendaylight.org/gerrit/#/c/16208
- https://github.com/opendaylight/openflowplugin
- https://web.archive.org/web/20150510044305/https://wiki.opendaylight.org/view/Security_Advisories#.5BModerate.5D_CVE-2015-1611_CVE-2015-1612_openflowplugin:_topology_spoofing_via_LLDP
- https://web.archive.org/web/20150701104709/https://www.internetsociety.org/sites/default/files/10_4_2.pdf
