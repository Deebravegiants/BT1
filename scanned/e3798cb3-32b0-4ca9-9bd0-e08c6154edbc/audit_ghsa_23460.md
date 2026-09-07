# [H] OpenFlow plugin for OpenDaylight allows spoofing the SDN topology

## Summary
Severity: High
Advisory: GHSA-49wf-927p-jpvj
CVE: CVE-2015-1611
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-49wf-927p-jpvj
Type: github-advisory

## Affected
- Maven: `org.opendaylight.openflowplugin:openflowplugin` — affected >=0 <0.0.6-Helium-SR3

## Details
OpenFlow plugin for OpenDaylight before Helium SR3 allows remote attackers to spoof the SDN topology and affect the flow of data, related to "fake LLDP injection."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1611
- https://git.opendaylight.org/gerrit/#/c/16193
- https://git.opendaylight.org/gerrit/#/c/16208
- https://github.com/opendaylight/openflowplugin
- https://web.archive.org/web/20150510044305/https://wiki.opendaylight.org/view/Security_Advisories#.5BModerate.5D_CVE-2015-1611_CVE-2015-1612_openflowplugin:_topology_spoofing_via_LLDP
- https://web.archive.org/web/20150701104709/https://www.internetsociety.org/sites/default/files/10_4_2.pdf
