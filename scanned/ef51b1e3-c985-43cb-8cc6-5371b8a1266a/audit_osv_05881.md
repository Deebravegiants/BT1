# [H] BIT-java-2022-21449

## Summary
Severity: High
Advisory: BIT-java-2022-21449
Aliases: BIT-java-min-2022-21449, BIT-jre-2022-21449, CVE-2022-21449
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2022-21449
Type: osv

## Affected
- Bitnami: `java` — affected >=18.0.0 <18.0.1

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Libraries). Supported versions that are affected are Oracle Java SE: 17.0.2 and 18; Oracle GraalVM Enterprise Edition: 21.3.1 and 22.0.0.2. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition. Successful attacks of this vulnerability can result in unauthorized creation, deletion or modification access to critical data or all Oracle Java SE, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS 3.1 Base Score 7.5 (Integrity impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N).

## References
- http://www.openwall.com/lists/oss-security/2022/04/28/2
- http://www.openwall.com/lists/oss-security/2022/04/28/3
- http://www.openwall.com/lists/oss-security/2022/04/28/4
- http://www.openwall.com/lists/oss-security/2022/04/28/5
- http://www.openwall.com/lists/oss-security/2022/04/28/6
- http://www.openwall.com/lists/oss-security/2022/04/28/7
- http://www.openwall.com/lists/oss-security/2022/04/29/1
- http://www.openwall.com/lists/oss-security/2022/04/30/1
- http://www.openwall.com/lists/oss-security/2022/04/30/2
- http://www.openwall.com/lists/oss-security/2022/04/30/3
- http://www.openwall.com/lists/oss-security/2022/04/30/4
- http://www.openwall.com/lists/oss-security/2022/05/01/1
- http://www.openwall.com/lists/oss-security/2022/05/01/2
- http://www.openwall.com/lists/oss-security/2022/05/02/1
- https://nvd.nist.gov/vuln/detail/CVE-2022-21449
- https://security.netapp.com/advisory/ntap-20220429-0006/
- https://www.debian.org/security/2022/dsa-5128
- https://www.debian.org/security/2022/dsa-5131
- https://www.oracle.com/security-alerts/cpuapr2022.html
