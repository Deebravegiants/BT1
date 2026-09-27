# [H] BIT-node-2021-22883

## Summary
Severity: High
Advisory: BIT-node-2021-22883
Aliases: BIT-node-min-2021-22883, CVE-2021-22883
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2021-22883
Type: osv

## Affected
- Bitnami: `node` — affected >=15.0.0 <15.10.0

## Details
Node.js before 10.24.0, 12.21.0, 14.16.0, and 15.10.0 is vulnerable to a denial of service attack when too many connection attempts with an 'unknownProtocol' are established. This leads to a leak of file descriptors. If a file descriptor limit is configured on the system, then the server is unable to accept new connections and prevent the process also from opening, e.g. a file. If no file descriptor limit is configured, then this lead to an excessive memory usage and cause the system to run out of memory.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://hackerone.com/reports/1043360
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E4FRS5ZVK4ZQ7XIJQNGIKUXG2DJFHLO7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F45Y7TXSU33MTKB6AGL2Q5V5ZOCNPKOG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HSYFUGKFUSZ27M5TEZ3FKILWTWFJTFAZ/
- https://nodejs.org/en/blog/vulnerability/february-2021-security-releases/
- https://security.netapp.com/advisory/ntap-20210416-0001/
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-22883
