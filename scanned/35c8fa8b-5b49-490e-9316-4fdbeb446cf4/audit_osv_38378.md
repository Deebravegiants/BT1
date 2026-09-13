# [H] FreeScout Customer Merge Cross-Mailbox Authorization Bypass

## Summary
Severity: High
Advisory: CVE-2026-39384
Aliases: GHSA-j6v9-22vq-53vh
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39384
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to 1.8.212, FreeScout does not take the limit_user_customer_visibility parameter into account when merging customers. This vulnerability is fixed in 1.8.212.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39384.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-j6v9-22vq-53vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-39384
- https://github.com/freescout-help-desk/freescout/commit/b395a1179117af5e2df704c6bad71feeb301b4ce
