# [M] Proxy component of Apache Pulsar subject to abuse as Denial of Service endpoint

## Summary
Severity: Medium
Advisory: GHSA-3mg9-m3f6-v7fq
CVE: CVE-2022-24280
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-3mg9-m3f6-v7fq
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar` — affected >=0 <2.7.5
- Maven: `org.apache.pulsar:pulsar` — affected >=2.8.0 <2.8.3
- Maven: `org.apache.pulsar:pulsar` — affected >=2.9.0 <2.9.2

## Details
Improper Input Validation vulnerability in Proxy component of Apache Pulsar allows an attacker to make TCP/IP connection attempts that originate from the Pulsar Proxy's IP address. When the Apache Pulsar Proxy component is used, it is possible to attempt to open TCP/IP connections to any IP address and port that the Pulsar Proxy can connect to. An attacker could use this as a way for DoS attacks that originate from the Pulsar Proxy's IP address. It hasn’t been detected that the Pulsar Proxy authentication can be bypassed. The attacker will have to have a valid token to a properly secured Pulsar Proxy. This issue affects Apache Pulsar Proxy versions 2.7.0 to 2.7.4; 2.8.0 to 2.8.2; 2.9.0 to 2.9.1; 2.6.4 and earlier.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24280
- https://github.com/apache/pulsar
- https://github.com/apache/pulsar/wiki/CVE-2022-24280
- https://lists.apache.org/thread/ghs9jtjfbpy4c6xcftyvkl6swznlom1v
