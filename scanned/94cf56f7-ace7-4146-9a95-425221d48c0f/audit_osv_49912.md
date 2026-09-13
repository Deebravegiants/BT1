# [M] CVE-2019-2977

## Summary
Severity: Medium
Advisory: CVE-2019-2977
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2019-10-16
Source: https://osv.dev/vulnerability/CVE-2019-2977
Type: osv

## Details
Vulnerability in the Java SE product of Oracle Java SE (component: Hotspot). Supported versions that are affected are Java SE: 11.0.4 and 13. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Java SE. Successful attacks of this vulnerability can result in unauthorized read access to a subset of Java SE accessible data and unauthorized ability to cause a partial denial of service (partial DOS) of Java SE. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets (in Java SE 8), that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.0 Base Score 4.8 (Confidentiality and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L).

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00066.html
- https://usn.ubuntu.com/4223-1/
- https://access.redhat.com/errata/RHSA-2019:3135
- https://seclists.org/bugtraq/2019/Oct/31
- https://security.netapp.com/advisory/ntap-20191017-0001/
- https://www.debian.org/security/2019/dsa-4546
- http://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
