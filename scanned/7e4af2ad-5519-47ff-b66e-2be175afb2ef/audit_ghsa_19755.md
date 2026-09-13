# [H] OpenDaylight SFC Insecure Shiro Cookie Configuration

## Summary
Severity: High
Advisory: GHSA-xp75-w7vq-5x6j
CVE: CVE-2025-29314
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-24
Source: https://github.com/advisories/GHSA-xp75-w7vq-5x6j
Type: github-advisory

## Affected
- Maven: `org.opendaylight.sfc:odl-sfc-ovs` — affected >=0
- Maven: `org.opendaylight.sfc:odl-sfc-openflow-renderer` — affected >=0

## Details
Insecure Shiro cookie configurations in OpenDaylight Service Function Chaining (SFC) Subproject SFC Sodium-SR4 and below allow attackers to access sensitive information via a man-in-the-middle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-29314
- https://blog.csdn.net/weixin_43959580/article/details/146018166
- https://github.com/opendaylight/sfc
