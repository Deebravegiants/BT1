# [H] CVE-2018-8030

## Summary
Severity: High
Advisory: CVE-2018-8030
Aliases: GHSA-7xr3-rgwh-pw22
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-20
Source: https://osv.dev/vulnerability/CVE-2018-8030
Type: osv

## Details
A Denial of Service vulnerability was found in Apache Qpid Broker-J versions 7.0.0-7.0.4 when AMQP protocols 0-8, 0-9 or 0-91 are used to publish messages with size greater than allowed maximum message size limit (100MB by default). The broker crashes due to the defect. AMQP protocols 0-10 and 1.0 are not affected.

## References
- https://lists.apache.org/thread.html/1089a4f351a1bdca0618199e53bceeec59a10bf4e3008018d6949876%40%3Cusers.qpid.apache.org%3E
- http://www.securitytracker.com/id/1041138
