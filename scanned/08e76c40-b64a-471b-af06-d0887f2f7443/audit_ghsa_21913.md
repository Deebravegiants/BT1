# [H] Improper Validation of Specified Quantity in Input in Eclipse Hono

## Summary
Severity: High
Advisory: GHSA-9f52-hpvw-v96w
CVE: CVE-2020-27217
CWE: CWE-1284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-9f52-hpvw-v96w
Type: github-advisory

## Affected
- Maven: `org.eclipse.hono:hono-core` — affected >=0 <1.4.3

## Details
In Eclipse Hono version 1.3.0 and 1.4.0 the AMQP protocol adapter does not verify the size of AMQP messages received from devices. In particular, a device may send messages that are bigger than the max-message-size that the protocol adapter has indicated during link establishment. While the AMQP 1.0 protocol explicitly disallows a peer to send such messages, a hand crafted AMQP 1.0 client could exploit this behavior in order to send a message of unlimited size to the adapter, eventually causing the adapter to fail with an out of memory exception.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27217
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=567068
