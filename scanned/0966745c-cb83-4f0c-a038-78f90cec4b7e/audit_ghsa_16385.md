# [H] Missing permission checks on Hazelcast client protocol

## Summary
Severity: High
Advisory: GHSA-xh6m-7cr7-xx66
CVE: CVE-2023-45859
CWE: CWE-281, CWE-922
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-02-27
Source: https://github.com/advisories/GHSA-xh6m-7cr7-xx66
Type: github-advisory

## Affected
- Maven: `com.hazelcast:hazelcast` — affected >=0
- Maven: `com.hazelcast:hazelcast` — affected >=4.2
- Maven: `com.hazelcast:hazelcast` — affected >=5.0
- Maven: `com.hazelcast:hazelcast` — affected >=5.1
- Maven: `com.hazelcast:hazelcast` — affected >=5.2.0 <5.2.5
- Maven: `com.hazelcast:hazelcast` — affected >=5.3.0 <5.3.5
- Maven: `com.hazelcast:hazelcast-all` — affected >=0
- Maven: `com.hazelcast:hazelcast-all` — affected >=4.2

## Details
### Impact
In Hazelcast through 4.1.10, 4.2 through 4.2.8, 5.0 through 5.0.5, 5.1 through 5.1.7, 5.2 through 5.2.4, and 5.3 through 5.3.2, some client operations don't check permissions properly, allowing authenticated users to access data stored in the cluster.

### Patches
Fix versions: 5.2.5, 5.3.5, 5.4.0-BETA-1

### Workarounds
There is no known workaround.

## References
- https://github.com/hazelcast/hazelcast/security/advisories/GHSA-xh6m-7cr7-xx66
- https://nvd.nist.gov/vuln/detail/CVE-2023-45859
- https://github.com/hazelcast/hazelcast/pull/25509
- https://github.com/hazelcast/hazelcast
