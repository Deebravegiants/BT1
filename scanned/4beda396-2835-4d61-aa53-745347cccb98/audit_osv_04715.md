# [H] Authorization Bypass Through User-Controlled Key in Kibana Leading to Unauthorized Information Disclosure and Case Attachment Integrity Compromise

## Summary
Severity: High
Advisory: BIT-elk-2026-56147
Aliases: BIT-kibana-2026-56147, CVE-2026-56147
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-elk-2026-56147
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.4.0 <9.4.3

## Details
Authorization Bypass Through User-Controlled Key (CWE-639) in Kibana can lead to unauthorized information disclosure and case attachment integrity compromise via Privilege Abuse (CAPEC-122). An inconsistency in Kibana's file access authorization logic allows a low-privileged authenticated user to retrieve, modify, and delete case attachments that belong to feature areas they are not authorized to access. Because the access control check and the resource retrieval use different resolution mechanisms, an authenticated attacker with limited file management permissions can obtain the contents of, modify, or delete protected case attachments — such as those associated with Security Solution cases — without holding the privileges required to access those features.

## References
- https://discuss.elastic.co/t/kibana-8-19-18-9-3-7-9-4-3-security-update-esa-2026-59/388558
- https://nvd.nist.gov/vuln/detail/CVE-2026-56147
