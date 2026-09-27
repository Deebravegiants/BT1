# [H] Apache ActiveMQ, Apache ActiveMQ All Module, Apache ActiveMQ MQTT Module: MQTT control packet remaining length field is not properly validated

## Summary
Severity: High
Advisory: BIT-activemq-2025-66168
Aliases: CVE-2025-66168, GHSA-c825-6ph3-4h84
Ecosystem: Bitnami
Published: 2026-03-06
Source: https://osv.dev/vulnerability/BIT-activemq-2025-66168
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.2.0 <6.2.1

## Details
WARNING:

Users of 6.x should upgrade to 6.2.4 or later as the fix was missed in previous 6.x releases.

See the  following for more details:
 https://activemq.apache.org/security-advisories.data/CVE-2026-40046-announcement.txt 
 https://www.cve.org/CVERecord?id=CVE-2026-40046 



Original Report:

Apache ActiveMQ does not properly validate the remaining length field which may lead to an overflow during the decoding of malformed packets. When this integer overflow occurs, ActiveMQ may incorrectly compute the total Remaining Length and subsequently misinterpret the payload as multiple MQTT control packets which makes the broker susceptible to unexpected behavior when interacting with non-compliant clients. This behavior violates the MQTT v3.1.1 specification, which restricts Remaining Length to a maximum of 4 bytes. The scenario occurs on established connections after the authentication process. Brokers that are not enabling mqtt transport connectors are not impacted.

This issue affects Apache ActiveMQ: before 5.19.2, 6.0.0 to 6.1.8, and 6.2.0

Users are recommended to upgrade to version 5.19.2, 6.1.9, or 6.2.1, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/03/03/5
- https://lists.apache.org/thread/13n8mkrb2jf2y6yyhpgrkmpqcm7djyto
- https://nvd.nist.gov/vuln/detail/CVE-2025-66168
- https://activemq.apache.org/security-advisories.data/CVE-2026-40046-announcement.txt
- https://www.cve.org/CVERecord?id=CVE-2026-40046
