# [M] Hazelcast vulnerable to unmasked password exposure

## Summary
Severity: Medium
Advisory: GHSA-5gj6-62g7-vmgf
CVE: CVE-2023-33264
CWE: CWE-200, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-22
Source: https://github.com/advisories/GHSA-5gj6-62g7-vmgf
Type: github-advisory

## Affected
- Maven: `com.hazelcast:hazelcast` — affected >=4.0-BETA-1
- Maven: `com.hazelcast:hazelcast` — affected >=5.0-BETA-1 <5.0.5
- Maven: `com.hazelcast:hazelcast` — affected >=5.1-BETA-1 <5.1.6
- Maven: `com.hazelcast:hazelcast` — affected >=5.2-BETA-1 <5.2.4
- Maven: `com.hazelcast:hazelcast` — affected >=5.3.0-BETA-1 <5.3.0

## Details
In Hazelcast before 5.3.0, configuration routines don't mask passwords in the member configuration properly. This allows Hazelcast Management Center users to view some of the secrets.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33264
- https://github.com/hazelcast/hazelcast/pull/24266
- https://github.com/hazelcast/hazelcast/pull/24266/commits/80a502d53cc48bf895711ab55f95e3a51e344ac1
- https://github.com/hazelcast/hazelcast/commit/74eed86c2b2b727148c442e98a01d0ca6941a49e
- https://github.com/hazelcast/hazelcast
