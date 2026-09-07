# [H] ONOS vulnerable to denial of service due to unrestricted NettyMessagingManager payload

## Summary
Severity: High
Advisory: GHSA-c6p7-vhw7-rc9w
CVE: CVE-2017-13763
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-c6p7-vhw7-rc9w
Type: github-advisory

## Affected
- Maven: `org.onosproject:onos-base` — affected >=1.8.0 <1.11.0

## Details
Open Network Operating System, ONOS, versions 1.8.0, 1.9.0, and 1.10.0 do not restrict the amount of memory allocated because the NettyMessagingManager payload size is not limited. ONOS nodes timeout when trying to connect to the cluster in vm test cluster, leading to a potential denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-13763
- https://github.com/opennetworkinglab/onos/commit/f7c7f6f229978fe4e78045069a4485504cc108c4
- https://gerrit.onosproject.org/#/c/13831
- https://gerrit.onosproject.org/#/c/14318
- https://github.com/opennetworkinglab/onos
- https://jira.onosproject.org/browse/ONOS-6401
