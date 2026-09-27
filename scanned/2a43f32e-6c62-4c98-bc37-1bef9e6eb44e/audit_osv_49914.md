# [M] CVE-2019-2999

## Summary
Severity: Medium
Advisory: CVE-2019-2999
CVSS: 4.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-10-16
Source: https://osv.dev/vulnerability/CVE-2019-2999
Type: osv

## Details
Vulnerability in the Java SE product of Oracle Java SE (component: Javadoc). Supported versions that are affected are Java SE: 7u231, 8u221, 11.0.4 and 13. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Java SE. Successful attacks require human interaction from a person other than the attacker and while the vulnerability is in Java SE, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of Java SE accessible data as well as unauthorized read access to a subset of Java SE accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets (in Java SE 8), that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.0 Base Score 4.7 (Confidentiality and Integrity impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N).

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00064.html
- https://access.redhat.com/errata/RHSA-2019:3158
- https://access.redhat.com/errata/RHSA-2019:4109
- https://access.redhat.com/errata/RHSA-2019:4110
- https://access.redhat.com/errata/RHSA-2019:4113
- https://www.debian.org/security/2019/dsa-4546
- https://access.redhat.com/errata/RHSA-2019:3134
- https://access.redhat.com/errata/RHSA-2019:3135
- https://access.redhat.com/errata/RHSA-2019:3136
- https://seclists.org/bugtraq/2019/Oct/27
- https://usn.ubuntu.com/4223-1/
- https://access.redhat.com/errata/RHSA-2019:3157
- https://access.redhat.com/errata/RHSA-2019:4115
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00066.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00031.html
- https://lists.debian.org/debian-lts-announce/2019/12/msg00005.html
- https://seclists.org/bugtraq/2019/Oct/31
- https://security.netapp.com/advisory/ntap-20191017-0001/
- https://www.debian.org/security/2019/dsa-4548
- http://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
