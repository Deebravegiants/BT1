# [C] Hikka vulnerable to RCE through edits in a channel

## Summary
Severity: Critical
Advisory: CVE-2025-52571
Aliases: GHSA-vwpq-wm8w-44wf
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-06-24
Source: https://osv.dev/vulnerability/CVE-2025-52571
Type: osv

## Details
Hikka is a Telegram userbot. A vulnerability affects all users of versions below 1.6.2, including most of the forks. It allows an unauthenticated attacker to gain access to Telegram account of a victim, as well as full access to the server. The issue is patched in version 1.6.2. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52571.json
- https://github.com/hikariatama/Hikka/security/advisories/GHSA-vwpq-wm8w-44wf
- https://nvd.nist.gov/vuln/detail/CVE-2025-52571
- https://github.com/hikariatama/Hikka/commit/9a0e4b1b387ef828c345c43d990421d5afcff5f6
