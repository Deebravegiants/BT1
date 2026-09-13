# [M] FreeScout: User Account Enumeration via Password Reset Response Differentiation

## Summary
Severity: Medium
Advisory: CVE-2026-45294
Aliases: GHSA-jvmv-2qcp-7855
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45294
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to 1.8.219, the password reset endpoint returns visually distinct responses depending on whether the submitted email address belongs to an existing user account, allowing unauthenticated attackers to enumerate valid helpdesk agent email addresses. This vulnerability is fixed in 1.8.219.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45294.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-jvmv-2qcp-7855
- https://nvd.nist.gov/vuln/detail/CVE-2026-45294
