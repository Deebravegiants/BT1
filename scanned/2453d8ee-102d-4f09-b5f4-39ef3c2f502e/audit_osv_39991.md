# [M] FreeScout: Thread Edit Authorization Bypass via Missing Mailbox Check

## Summary
Severity: Medium
Advisory: CVE-2026-48810
Aliases: GHSA-3w38-h42v-3h6w
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-48810
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to 1.8.221, while investigating the ThreadPolicy::delete issue reported previously, the same missing mailbox membership check was found in the sibling ThreadPolicy::edit method. A user with the PERM_EDIT_CONVERSATIONS permission who created a message or internal note in Mailbox A can rewrite that thread's body after an administrator removes them from Mailbox A, because the policy checks only authorship and a global permission flag — not current mailbox membership. This vulnerability is fixed in 1.8.221.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48810.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-3w38-h42v-3h6w
- https://nvd.nist.gov/vuln/detail/CVE-2026-48810
