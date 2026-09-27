# [M] FreeScout's Missing Authorization in load_customer_info Allows Any Authenticated User to Access Full Customer PII

## Summary
Severity: Medium
Advisory: CVE-2026-40570
Aliases: GHSA-w77q-wjfp-c822
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40570
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.213, the `load_customer_info` action in `POST /conversation/ajax` returns complete customer profile data to any authenticated user without verifying mailbox access. An attacker only needs a valid email address to retrieve all customer PII. Version 1.8.213 fixes the issue.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.213
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40570.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-w77q-wjfp-c822
- https://nvd.nist.gov/vuln/detail/CVE-2026-40570
- https://github.com/freescout-help-desk/freescout/commit/f35b4249c72d9bdac6ab1ea4e288f5894be34057
