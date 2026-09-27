# [H] Apache Tomcat h2c request mix-up

## Summary
Severity: High
Advisory: BIT-tomcat-2021-25122
Aliases: CVE-2021-25122, GHSA-j39c-c8hj-x4j3
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tomcat-2021-25122
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=10.0.0 <10.0.1

## Details
When responding to new h2c connection requests, Apache Tomcat versions 9.0.0 through 9.0.41 and 8.5.0 to 8.5.61 could duplicate request headers and a limited amount of request body from one request to another meaning user A and user B could both see the results of user A's request.

## References
- http://www.openwall.com/lists/oss-security/2021/03/01/1
- https://lists.apache.org/thread.html/r7b95bc248603360501f18c8eb03bb6001ec0ee3296205b34b07105b7%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r7b95bc248603360501f18c8eb03bb6001ec0ee3296205b34b07105b7%40%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r7b95bc248603360501f18c8eb03bb6001ec0ee3296205b34b07105b7%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r7b95bc248603360501f18c8eb03bb6001ec0ee3296205b34b07105b7%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rcd90bf36b1877e1310b87ecd14ed7bbb15da52b297efd9f0e7253a3b%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rd0463f9a5cbc02a485404c4b990f0da452e5ac5c237808edba11c947%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rf6d5d57b114678d8898005faef31e9fd6d7c981fcc4ccfc3bc272fc9%40%3Cdev.tomcat.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/03/msg00018.html
- https://security.gentoo.org/glsa/202208-34
- https://security.netapp.com/advisory/ntap-20210409-0002/
- https://www.debian.org/security/2021/dsa-4891
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-25122
