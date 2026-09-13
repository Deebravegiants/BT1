# [H] BIT-nginx-2021-23017

## Summary
Severity: High
Advisory: BIT-nginx-2021-23017
Aliases: BIT-nginx-gateway-2021-23017, CVE-2021-23017
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-nginx-2021-23017
Type: osv

## Affected
- Bitnami: `nginx` — affected >=0.6.18 <1.20.1

## Details
A security issue in nginx resolver was identified, which might allow an attacker who is able to forge UDP packets from the DNS server to cause 1-byte memory overwrite, resulting in worker process crash or potential other impact.

## References
- http://mailman.nginx.org/pipermail/nginx-announce/2021/000300.html
- http://packetstormsecurity.com/files/167720/Nginx-1.20.0-Denial-Of-Service.html
- https://lists.apache.org/thread.html/r37e6b2165f7c910d8e15fd54f4697857619ad2625f56583802004009%40%3Cnotifications.apisix.apache.org%3E
- https://lists.apache.org/thread.html/r4d4966221ca399ce948ef34884652265729d7d9ef8179c78d7f17e7f%40%3Cnotifications.apisix.apache.org%3E
- https://lists.apache.org/thread.html/r6fc5c57b38e93e36213e9a18c8a4e5dbd5ced1c7e57f08a1735975ba%40%3Cnotifications.apisix.apache.org%3E
- https://lists.apache.org/thread.html/rf232eecd47fdc44520192810560303073cefd684b321f85e311bad31%40%3Cnotifications.apisix.apache.org%3E
- https://lists.apache.org/thread.html/rf318aeeb4d7a3a312734780b47de83cefb7e6995da0b2cae5c28675c%40%3Cnotifications.apisix.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7SFVYHC7OXTEO4SMBWXDVK6E5IMEYMEE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GNKOP2JR5L7KCIZTJRZDCUPJTUONMC5I/
- https://security.netapp.com/advisory/ntap-20210708-0006/
- https://support.f5.com/csp/article/K12331123%2C
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-23017
