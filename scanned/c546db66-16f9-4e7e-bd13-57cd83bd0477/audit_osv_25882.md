# [M] CVE-2023-46658

## Summary
Severity: Medium
Advisory: CVE-2023-46658
Aliases: GHSA-2xpq-5952-38w3
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-46658
Type: osv

## Details
Jenkins MSTeams Webhook Trigger Plugin 0.1.1 and earlier uses a non-constant time comparison function when checking whether the provided and expected webhook token are equal, potentially allowing attackers to use statistical methods to obtain a valid webhook token.

## References
- https://www.jenkins.io/security/advisory/2023-10-25/#SECURITY-2876
- http://www.openwall.com/lists/oss-security/2023/10/25/2
