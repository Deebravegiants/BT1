# [M] BIT-java-2020-2655

## Summary
Severity: Medium
Advisory: BIT-java-2020-2655
Aliases: BIT-java-min-2020-2655, BIT-jre-2020-2655, CVE-2020-2655
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2020-2655
Type: osv

## Affected
- Bitnami: `java` — affected >=13.0.1

## Details
Vulnerability in the Java SE product of Oracle Java SE (component: JSSE). Supported versions that are affected are Java SE: 11.0.5 and 13.0.1. Difficult to exploit vulnerability allows unauthenticated attacker with network access via HTTPS to compromise Java SE. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of Java SE accessible data as well as unauthorized read access to a subset of Java SE accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets (in Java SE 8), that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS 3.0 Base Score 4.8 (Confidentiality and Integrity impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00050.html
- https://access.redhat.com/errata/RHSA-2020:0122
- https://access.redhat.com/errata/RHSA-2020:0128
- https://access.redhat.com/errata/RHSA-2020:0232
- https://nvd.nist.gov/vuln/detail/CVE-2020-2655
- https://seclists.org/bugtraq/2020/Jan/24
- https://security.netapp.com/advisory/ntap-20200122-0003/
- https://usn.ubuntu.com/4257-1/
- https://www.debian.org/security/2020/dsa-4605
- https://www.oracle.com/security-alerts/cpujan2020.html
