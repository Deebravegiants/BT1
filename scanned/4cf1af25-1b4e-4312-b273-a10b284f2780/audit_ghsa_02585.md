# [C] Hessian protocol configuration vulnerability in Apache Dubbo

## Summary
Severity: Critical
Advisory: GHSA-cpx9-4rwv-486v
CVE: CVE-2021-36163
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-08
Source: https://github.com/advisories/GHSA-cpx9-4rwv-486v
Type: github-advisory

## Affected
- Maven: `org.apache.dubbo:dubbo` — affected >=2.7.0 <2.7.13
- Maven: `org.apache.dubbo:dubbo` — affected >=0 <2.6.10.1

## Details
In Apache Dubbo, users may choose to use the Hessian protocol. The Hessian protocol is implemented on top of HTTP and passes the body of a POST request directly to a HessianSkeleton: New HessianSkeleton are created without any configuration of the serialization factory and therefore without applying the dubbo properties for applying allowed or blocked type lists. In addition, the generic service is always exposed and therefore attackers do not need to figure out a valid service/method name pair. This is fixed in 2.7.13, 2.6.10.1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36163
- https://github.com/apache/dubbo/pull/8238
- https://github.com/apache/dubbo
- https://github.com/apache/dubbo/releases/tag/dubbo-2.6.10.1
- https://github.com/apache/dubbo/releases/tag/dubbo-2.7.13
- https://lists.apache.org/thread.html/r8d0adc057bb15a37199502cc366f4b1164c9c536ce28e4defdb428c0%40%3Cdev.dubbo.apache.org%3E
