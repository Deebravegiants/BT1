# [C] Tautulli: RCE via eval() sandbox bypass using lambda nested scope to escape co_names whitelist check

## Summary
Severity: Critical
Advisory: CVE-2026-28505
Aliases: GHSA-m62j-gwm9-7p8m
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-28505
Type: osv

## Details
Tautulli is a Python based monitoring and tracking tool for Plex Media Server. Prior to version 2.17.0, the str_eval() function in notification_handler.py implements a sandboxed eval() for notification text templates. The sandbox attempts to restrict callable names by inspecting code.co_names of the compiled code object. However, co_names only contains names from the outer code object. When a lambda expression is used, it creates a nested code object whose attribute accesses are stored in code.co_consts, NOT in code.co_names. The sandbox never inspects nested code objects. This issue has been patched in version 2.17.0.

## References
- https://github.com/Tautulli/Tautulli/releases/tag/v2.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28505.json
- https://github.com/Tautulli/Tautulli/security/advisories/GHSA-m62j-gwm9-7p8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-28505
