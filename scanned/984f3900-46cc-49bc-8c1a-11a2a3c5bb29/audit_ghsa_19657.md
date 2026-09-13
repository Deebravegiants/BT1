# [H] OpenDaylight SFC Denial of Service (DoS)

## Summary
Severity: High
Advisory: GHSA-v3vp-fg2v-g7q4
CVE: CVE-2025-29313
CWE: CWE-404
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-24
Source: https://github.com/advisories/GHSA-v3vp-fg2v-g7q4
Type: github-advisory

## Affected
- Maven: `org.opendaylight.sfc:odl-sfc-openflow-renderer` — affected >=0
- Maven: `org.opendaylight.sfc:odl-sfc-ovs` — affected >=0

## Details
Use of incorrectly resolved name or reference in OpenDaylight Service Function Chaining (SFC) Subproject SFC Sodium-SR4 and below allows attackers to cause a Denial of Service (DoS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-29313
- https://blog.csdn.net/weixin_43959580/article/details/146018191
- https://github.com/opendaylight/sfc
