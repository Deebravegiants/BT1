# [H] BIT-wildfly-2020-10718

## Summary
Severity: High
Advisory: BIT-wildfly-2020-10718
Aliases: CVE-2020-10718
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-wildfly-2020-10718
Type: osv

## Affected
- Bitnami: `wildfly` — affected >=0 <13.0.0

## Details
A flaw was found in Wildfly before wildfly-embedded-13.0.0.Final, where the embedded managed process API has an exposed setting of the Thread Context Classloader (TCCL). This setting is exposed as a public method, which can bypass the security manager. The highest threat from this vulnerability is to confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1828476
- https://nvd.nist.gov/vuln/detail/CVE-2020-10718
