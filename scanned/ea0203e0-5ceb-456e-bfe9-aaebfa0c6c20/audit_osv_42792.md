# [H] Subrion CMS Admin Grid SQL Injection via Unwhitelisted ORDER BY sort Parameter

## Summary
Severity: High
Advisory: CVE-2026-71292
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71292
Type: osv

## Details
Subrion CMS's admin grid sorting helper, _gridGetSorting in includes/classes/ia.base.controller.admin.php, whitelists the (ASC/DESC) request parameter via in_array, but falls back to the raw, attacker-supplied GET parameter whenever the requested key is not present in the per-controller whitelist array: , which is then placed into %s with only backtick-quoting and no escaping.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71292.json
- https://github.com/intelliants/subrion
- https://github.com/intelliants/subrion/blob/master/includes/classes/ia.base.controller.admin.php
- https://nvd.nist.gov/vuln/detail/CVE-2026-71292
