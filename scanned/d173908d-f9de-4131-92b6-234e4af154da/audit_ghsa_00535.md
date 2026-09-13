# [H] In Bouncy Castle JCE Provider the DSA key pair generator generates a weak private key if used with default values

## Summary
Severity: High
Advisory: GHSA-rrvx-pwf8-p59p
CVE: CVE-2016-1000343
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-rrvx-pwf8-p59p
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=0 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15` — affected >=0 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0 <1.56

## Details
In the Bouncy Castle JCE Provider version 1.55 and earlier the DSA key pair generator generates a weak private key if used with default values. If the JCA key pair generator is not explicitly initialised with DSA parameters, 1.55 and earlier generates a private value assuming a 1024 bit key size. In earlier releases this can be dealt with by explicitly passing parameters to the key pair generator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000343
- https://github.com/bcgit/bc-java/commit/50a53068c094d6cff37659da33c9b4505becd389#diff-5578e61500abb2b87b300d3114bdfd7d
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2018:2927
- https://github.com/advisories/GHSA-rrvx-pwf8-p59p
- https://github.com/bcgit/bc-java
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451@%3Csolr-user.lucene.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2018/07/msg00009.html
- https://security.netapp.com/advisory/ntap-20181127-0004
- https://usn.ubuntu.com/3727-1
- https://www.oracle.com/security-alerts/cpuoct2020.html
