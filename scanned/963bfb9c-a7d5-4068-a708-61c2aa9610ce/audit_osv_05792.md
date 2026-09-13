# [H] BIT-haproxy-2021-40346

## Summary
Severity: High
Advisory: BIT-haproxy-2021-40346
Aliases: CVE-2021-40346
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-haproxy-2021-40346
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=2.4.0 <2.4.4

## Details
An integer overflow exists in HAProxy 2.0 through 2.5 in htx_add_header that can be exploited to perform an HTTP request smuggling attack, allowing an attacker to bypass all configured http-request HAProxy ACLs and possibly other ACLs.

## References
- https://git.haproxy.org/?p=haproxy.git
- https://github.com/haproxy/haproxy/commit/3b69886f7dcc3cfb3d166309018e6cfec9ce2c95
- https://jfrog.com/blog/critical-vulnerability-in-haproxy-cve-2021-40346-integer-overflow-enables-http-smuggling/
- https://lists.apache.org/thread.html/r284567dd7523f5823e2ce995f787ccd37b1cc4108779c50a97c79120%40%3Cdev.cloudstack.apache.org%3E
- https://lists.apache.org/thread.html/r8a58fd7a29808e5d27ee56877745e58dc4bb041b9af94601554e2a5a%40%3Cdev.cloudstack.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A7V2IYO22LWVBGUNZWVKNTMDV4KINLFO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MXTSBY2TEAXWZVFQM3CXHJFRONX7PEMN/
- https://www.debian.org/security/2021/dsa-4968
- https://www.mail-archive.com/haproxy%40formilux.org
- https://www.mail-archive.com/haproxy%40formilux.org/msg41114.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-40346
