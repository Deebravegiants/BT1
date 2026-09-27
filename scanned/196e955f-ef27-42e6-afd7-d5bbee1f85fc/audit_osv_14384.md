# [H] CVE-2019-0200

## Summary
Severity: High
Advisory: CVE-2019-0200
Aliases: GHSA-c9h6-xhg9-xxrv
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-06
Source: https://osv.dev/vulnerability/CVE-2019-0200
Type: osv

## Details
A Denial of Service vulnerability was found in Apache Qpid Broker-J versions 6.0.0-7.0.6 (inclusive) and 7.1.0 which allows an unauthenticated attacker to crash the broker instance by sending specially crafted commands using AMQP protocol versions below 1.0 (AMQP 0-8, 0-9, 0-91 and 0-10). Users of Apache Qpid Broker-J versions 6.0.0-7.0.6 (inclusive) and 7.1.0 utilizing AMQP protocols 0-8, 0-9, 0-91, 0-10 must upgrade to Qpid Broker-J versions 7.0.7 or 7.1.1 or later.

## References
- https://lists.apache.org/thread.html/ac79d48de37d42b64da50384dbe9c8a329c5f553dd12ef7c28a832de%40%3Cusers.qpid.apache.org%3E
- http://www.securityfocus.com/bid/107215
