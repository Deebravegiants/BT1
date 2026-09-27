# [H] LinkAce: Password Reset Poisoning via X-Forwarded-Host Header Injection Leading to Account Takeover

## Summary
Severity: High
Advisory: CVE-2026-40905
Aliases: GHSA-48wv-jpf4-vjfv
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40905
Type: osv

## Details
LinkAce is a self-hosted archive to collect website links. Prior to 2.5.4, a password reset poisoning vulnerability was identified in the application due to improper trust of user-controlled HTTP headers. The application uses the X-Forwarded-Host header when generating password reset URLs. By manipulating this header during a password reset request, an attacker can inject an attacker-controlled domain into the reset link sent via email. As a result, the victim receives a password reset email containing a malicious link pointing to an attacker-controlled domain. When the victim clicks the link, the password reset token is transmitted to the attacker-controlled server. An attacker can capture this token and use it to reset the victim’s password, leading to full account takeover. This vulnerability is fixed in 2.5.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40905.json
- https://github.com/Kovah/LinkAce/security/advisories/GHSA-48wv-jpf4-vjfv
- https://nvd.nist.gov/vuln/detail/CVE-2026-40905
