# [C] Hazelcast connection caching

## Summary
Severity: Critical
Advisory: GHSA-c5hg-mr8r-f6jp
CVE: CVE-2022-36437
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-c5hg-mr8r-f6jp
Type: github-advisory

## Affected
- Maven: `com.hazelcast:hazelcast` — affected >=0 <3.12.13
- Maven: `com.hazelcast:hazelcast` — affected >=4.0
- Maven: `com.hazelcast:hazelcast` — affected >=4.1 <4.1.10
- Maven: `com.hazelcast:hazelcast` — affected >=4.2 <4.2.6
- Maven: `com.hazelcast:hazelcast` — affected >=5.0 <5.0.4
- Maven: `com.hazelcast:hazelcast` — affected >=5.1 <5.1.3
- Maven: `com.hazelcast.jet:hazelcast-jet` — affected >=0 <4.5.4
- Maven: `com.hazelcast.jet:hazelcast-jet-enterprise` — affected >=0 <4.5.4
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=0 <3.12.13
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=4.0
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=4.1 <4.1.10
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=4.2 <4.2.6
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=5.0 <5.0.4
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=5.1 <5.1.3

## Details
### Impact
The Connection handler in Hazelcast and Hazelcast Jet allows an unauthenticated, remote attacker to access and manipulate data in the cluster with another authenticated connection's identity.
The affected Hazelcast versions are through 3.12.12, 4.0.6, 4.1.9, 4.2.5, 5.0.3, and 5.1.2.
The affected Hazelcast Jet versions are through 4.5.3.

### Patches
Hazelcast Jet (and Enterprise) 4.5.4.
Hazelcast IMDG (and Enterprise)3.12.13
Hazelcast IMDG (and Enterprise) 4.1.10
Hazelcast IMDG (and Enterprise) 4.2.6
Hazelcast Platform (and Enterprise) 5.1.3

### Workarounds
There is no known workaround, but setups with TLS and mutual authentication enabled significantly lowers the exploitation risk.

### References
https://support.hazelcast.com/s/article/Security-Advisory-for-CVE-2022-36437

## References
- https://github.com/hazelcast/hazelcast/security/advisories/GHSA-c5hg-mr8r-f6jp
- https://nvd.nist.gov/vuln/detail/CVE-2022-36437
- https://github.com/hazelcast/hazelcast
- https://support.hazelcast.com/s/article/Security-Advisory-for-CVE-2022-36437
