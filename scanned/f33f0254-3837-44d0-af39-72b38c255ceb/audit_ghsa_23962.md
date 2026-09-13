# [H] Deserialization of Untrusted Data in Hazelcast

## Summary
Severity: High
Advisory: GHSA-jv65-pf7v-f7p8
CVE: CVE-2016-10750
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jv65-pf7v-f7p8
Type: github-advisory

## Affected
- Maven: `com.hazelcast:hazelcast` — affected >=0 <3.11

## Details
In Hazelcast before 3.11, the cluster join procedure is vulnerable to remote code execution via Java deserialization. If an attacker can reach a listening Hazelcast instance with a crafted JoinRequest, and vulnerable classes exist in the classpath, the attacker can run arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10750
- https://github.com/hazelcast/hazelcast/issues/8024
- https://github.com/hazelcast/hazelcast/pull/12230
