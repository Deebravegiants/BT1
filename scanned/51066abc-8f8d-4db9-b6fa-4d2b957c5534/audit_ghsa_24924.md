# [H] Docker image code execution with Apache Mesos

## Summary
Severity: High
Advisory: GHSA-32w9-2qpc-5f9v
CVE: CVE-2019-0204
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-32w9-2qpc-5f9v
Type: github-advisory

## Affected
- Maven: `org.apache.mesos:mesos` — affected >=0 <1.4.3
- Maven: `org.apache.mesos:mesos` — affected >=1.5.0 <1.5.3
- Maven: `org.apache.mesos:mesos` — affected >=1.6.0 <1.6.2
- Maven: `org.apache.mesos:mesos` — affected >=1.7.0 <1.7.2

## Details
A specifically crafted Docker image running under the root user can overwrite the init helper binary of the container runtime and/or the command executor in Apache Mesos versions pre-1.4.x, 1.4.0 to 1.4.2, 1.5.0 to 1.5.2, 1.6.0 to 1.6.1, and 1.7.0 to 1.7.1. A malicious actor can therefore gain root-level code execution on the host.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0204
- https://access.redhat.com/errata/RHSA-2019:3892
- https://lists.apache.org/thread.html/b162dd624dc088cd634292f0402282a1d1d0ce853baeae8205bc033c@%3Cdev.mesos.apache.org%3E
- http://www.securityfocus.com/bid/107605
