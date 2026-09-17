# [C] mailcow: dockerized vulnerable to SSTI in Quota and Quarantine Notification Template

## Summary
Severity: Critical
Advisory: CVE-2025-53909
Aliases: GHSA-8p7g-6cjj-wr9m
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/CVE-2025-53909
Type: osv

## Details
mailcow: dockerized is an open source groupware/email suite based on docker. A Server-Side Template Injection (SSTI) vulnerability exists in versions prior to 2025-07 in the notification template system used by mailcow for sending quota and quarantine alerts. The template rendering engine allows template expressions that may be abused to execute code in certain contexts. The issue requires admin-level access to mailcow UI to configure templates, which are automatically rendered during normal system operation. Version 2025-07 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53909.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-8p7g-6cjj-wr9m
- https://nvd.nist.gov/vuln/detail/CVE-2025-53909
- https://github.com/mailcow/mailcow-dockerized/commit/8c5f6c03214a4b2bdbf3c78932f860eee949012b
