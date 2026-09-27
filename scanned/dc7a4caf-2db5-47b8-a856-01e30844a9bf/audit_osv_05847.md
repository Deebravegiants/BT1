# [H] BIT-java-2020-2816

## Summary
Severity: High
Advisory: BIT-java-2020-2816
Aliases: BIT-java-min-2020-2816, BIT-jre-2020-2816, CVE-2020-2816
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2020-2816
Type: osv

## Affected
- Bitnami: `java` — affected >=12.0.0 <14.0.1

## Details
Vulnerability in the Java SE product of Oracle Java SE (component: JSSE). Supported versions that are affected are Java SE: 11.0.6 and 14. Easily exploitable vulnerability allows unauthenticated attacker with network access via HTTPS to compromise Java SE. Successful attacks of this vulnerability can result in unauthorized creation, deletion or modification access to critical data or all Java SE accessible data. Note: This vulnerability can only be exploited by supplying data to APIs in the specified Component without using Untrusted Java Web Start applications or Untrusted Java applets, such as through a web service. CVSS 3.0 Base Score 7.5 (Integrity impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00000.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-2816
- https://security.netapp.com/advisory/ntap-20200416-0004/
- https://usn.ubuntu.com/4337-1/
- https://www.debian.org/security/2020/dsa-4662
- https://www.oracle.com/security-alerts/cpuapr2020.html
