# [H] LinkAce Vulnerable to Stored XSS on the Audit Page

## Summary
Severity: High
Advisory: CVE-2025-59424
Aliases: GHSA-289g-9gff-p4wh
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2025-59424
Type: osv

## Details
LinkAce is a self-hosted archive to collect website links. Prior to 2.3.1, a Stored Cross-Site Scripting (XSS) vulnerability has been identified on the /system/audit page. The application fails to properly sanitize the username field before it is rendered in the audit log. An authenticated attacker can set a malicious JavaScript payload as their username. When an action performed by this user is recorded (e.g., generate or revoke an API token), the payload is stored in the database. The script is then executed in the browser of any user, particularly administrators, who views the /system/audit page. This vulnerability is fixed in 2.3.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59424.json
- https://github.com/Kovah/LinkAce/security/advisories/GHSA-289g-9gff-p4wh
- https://nvd.nist.gov/vuln/detail/CVE-2025-59424
- https://github.com/Kovah/LinkAce/commit/c0d21b974b32f1ca2fab550fb476c573a068e196
