# [M] Apache Pulsar Broker Improper Authentication vulnerability

## Summary
Severity: Medium
Advisory: GHSA-47r2-phr8-m8cp
CVE: CVE-2023-31007
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-47r2-phr8-m8cp
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=2.9.0 <2.10.4
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=2.11.0 <2.11.1

## Details
Improper Authentication vulnerability in Apache Software Foundation Apache Pulsar Broker allows a client to stay connected to a broker after authentication data expires if the client connected through the Pulsar Proxy when the broker is configured with authenticateOriginalAuthData=false or if a client connects directly to a broker with a specially crafted connect command when the broker is configured with authenticateOriginalAuthData=false.

This issue affects Apache Pulsar: through 2.9.4, from 2.10.0 through 2.10.3, 2.11.0.

2.9 Pulsar Broker users should upgrade to at least 2.9.5.
2.10 Pulsar Broker users should upgrade to at least 2.10.4.
2.11 Pulsar Broker users should upgrade to at least 2.11.1.
3.0 Pulsar Broker users are unaffected.
Any users running the Pulsar Broker for 2.8.* and earlier should upgrade to one of the above patched versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31007
- https://github.com/apache/pulsar
- https://lists.apache.org/thread/qxn99xxyp0zv6jchjggn3soyo5gvqfxj
