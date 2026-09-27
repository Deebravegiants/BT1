# [H] OpenNMS Horizon RCE via Unsafe Deserialization

## Summary
Severity: High
Advisory: GHSA-853f-x27w-8r74
CVE: CVE-2020-12760
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-853f-x27w-8r74
Type: github-advisory

## Affected
- Maven: `org.opennms.core:org.opennms.core.daemon` — affected >=0 <26.0.1

## Details
An issue was discovered in OpenNMS Horizon before 26.0.1, and Meridian before 2018.1.19 and 2019 before 2019.1.7. The ActiveMQ channel configuration allowed for arbitrary deserialization of Java objects (aka ActiveMQ Minion payload deserialization), leading to remote code execution for any authenticated channel user regardless of its assigned permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12760
- https://github.com/OpenNMS/opennms/pull/2983
- https://github.com/OpenNMS/opennms/commit/e21fc14ce355533493da0db815bd81a66e291382
- https://github.com/OpenNMS/opennms
- https://github.com/OpenNMS/opennms/releases/tag/opennms-26.0.1-1
- https://issues.opennms.org/browse/NMS-12673
- https://www.opennms.com/en/blog/2020-04-29-opennms-horizon-26-0-1-luchador-released
- https://www.opennms.com/en/blog/2020-04-29-opennms-meridian-2018-1-18-wildfire-released
- https://www.opennms.com/en/blog/2020-04-29-opennms-meridian-2019-1-6-europa-released
