# [M] CVE-2022-21496

## Summary
Severity: Medium
Advisory: CVE-2022-21496
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-04-19
Source: https://osv.dev/vulnerability/CVE-2022-21496
Type: osv

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: JNDI). Supported versions that are affected are Oracle Java SE: 7u331, 8u321, 11.0.14, 17.0.2, 18; Oracle GraalVM Enterprise Edition: 20.3.5, 21.3.1 and 22.0.0.2. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of Oracle Java SE, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS 3.1 Base Score 5.3 (Integrity impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N).

## References
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21496.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-21496
- https://security.netapp.com/advisory/ntap-20220429-0006/
- https://security.netapp.com/advisory/ntap-20240621-0006/
- https://www.debian.org/security/2022/dsa-5128
- https://www.debian.org/security/2022/dsa-5131
- https://lists.debian.org/debian-lts-announce/2022/05/msg00017.html
