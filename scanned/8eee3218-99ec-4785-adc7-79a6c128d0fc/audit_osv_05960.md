# [H] BIT-java-2026-21945

## Summary
Severity: High
Advisory: BIT-java-2026-21945
Aliases: BIT-java-min-2026-21945, BIT-jre-2026-21945, CVE-2026-21945
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2026-21945
Type: osv

## Affected
- Bitnami: `java` — affected >=22.0.0 <25.0.2

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Security).  Supported versions that are affected are Oracle Java SE: 8u471, 8u471-b50, 8u471-perf, 11.0.29, 17.0.17, 21.0.9, 25.0.1; Oracle GraalVM for JDK: 17.0.17 and  21.0.9; Oracle GraalVM Enterprise Edition: 21.3.16. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.1 Base Score 7.5 (Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-21945
- https://www.oracle.com/security-alerts/cpujan2026.html
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://access.redhat.com/errata/RHSA-2026:0847
- https://access.redhat.com/errata/RHSA-2026:0848
- https://access.redhat.com/errata/RHSA-2026:0895
- https://access.redhat.com/errata/RHSA-2026:0897
- https://access.redhat.com/errata/RHSA-2026:0899
- https://access.redhat.com/errata/RHSA-2026:0901
- https://access.redhat.com/errata/RHSA-2026:0927
- https://access.redhat.com/errata/RHSA-2026:0928
- https://access.redhat.com/errata/RHSA-2026:0931
- https://access.redhat.com/errata/RHSA-2026:0932
- https://access.redhat.com/errata/RHSA-2026:0933
- https://access.redhat.com/errata/RHSA-2026:1606
- https://access.redhat.com/errata/RHSA-2026:4832
- https://access.redhat.com/security/cve/CVE-2026-21945
- https://bugzilla.redhat.com/show_bug.cgi?id=2429927
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-21945.json
