# [M] BIT-wildfly-2020-14317

## Summary
Severity: Medium
Advisory: BIT-wildfly-2020-14317
Aliases: CVE-2020-14317
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-wildfly-2020-14317
Type: osv

## Affected
- Bitnami: `wildfly` — affected unspecified

## Details
It was found that the issue for security flaw CVE-2019-3805 appeared again in a further version of JBoss Enterprise Application Platform - Continuous Delivery (EAP-CD) introducing regression. An attacker could exploit this by modifying the PID file in /var/run/jboss-eap/ allowing the init.d script to terminate any process as root.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1854251
