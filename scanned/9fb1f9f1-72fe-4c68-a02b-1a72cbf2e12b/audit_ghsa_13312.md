# [C] Apache Pulsar Incorrect Authorization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-g9cv-v3v4-3h8r
CVE: CVE-2023-30429
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-g9cv-v3v4-3h8r
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar` — affected >=0 <2.10.4
- Maven: `org.apache.pulsar:pulsar` — affected >=2.11.0 <2.11.1

## Details
Incorrect Authorization vulnerability in Apache Software Foundation Apache Pulsar.

This issue affects Apache Pulsar: before 2.10.4, and 2.11.0.

When a client connects to the Pulsar Function Worker via the Pulsar Proxy where the Pulsar Proxy uses mTLS authentication to authenticate with the Pulsar Function Worker, the Pulsar Function Worker incorrectly performs authorization by using the Proxy's role for authorization instead of the client's role, which can lead to privilege escalation, especially if the proxy is configured with a superuser role.

The recommended mitigation for impacted users is to upgrade the Pulsar Function Worker to a patched version.

2.10 Pulsar Function Worker users should upgrade to at least 2.10.4.
2.11 Pulsar Function Worker users should upgrade to at least 2.11.1.
3.0 Pulsar Function Worker users are unaffected.
Any users running the Pulsar Function Worker for 2.9.* and earlier should upgrade to one of the above patched versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30429
- https://github.com/apache/pulsar
- https://lists.apache.org/thread/v0gcvvxswr830314q4b1kybsfmcf3jf8
