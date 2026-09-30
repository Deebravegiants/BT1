# [H] Deserialization of Untrusted Data in Apache Heron

## Summary
Severity: High
Advisory: GHSA-hjgm-f7vx-m5g7
CVE: CVE-2020-1964
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-hjgm-f7vx-m5g7
Type: github-advisory

## Affected
- Maven: `org.apache.heron:heron-simulator` — affected >=0.20.0-incubating <0.20.3-incubating

## Details
It was noticed that Apache Heron 0.20.2-incubating, Release 0.20.1-incubating, and Release v-0.20.0-incubating does not configure its YAML parser to prevent the instantiation of arbitrary types, resulting in a remote code execution vulnerabilities (CWE-502: Deserialization of Untrusted Data).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1964
- https://lists.apache.org/thread.html/r16dd39f4180e4443ef4ca774a3a5a3d7ac69f91812c183ed2a99e959%40%3Cdev.heron.apache.org%3E
- https://lists.apache.org/thread.html/rd43ae18588fd7bdb375be63bc95a651aab319ced6306759e1237ce67@%3Cdev.ignite.apache.org%3E
- https://lists.apache.org/thread.html/re7b43cf8333ee30b6589e465f72a6ed4a082222612d1a0fdd30beb94@%3Cdev.ignite.apache.org%3E
- https://lists.apache.org/thread.html/re7b43cf8333ee30b6589e465f72a6ed4a082222612d1a0fdd30beb94@%3Cuser.ignite.apache.org%3E
- https://lists.apache.org/thread.html/rf032a13a4711f88c0a2c0734eecbee1026cc1b6cde27d16a653f8755@%3Cdev.ignite.apache.org%3E
