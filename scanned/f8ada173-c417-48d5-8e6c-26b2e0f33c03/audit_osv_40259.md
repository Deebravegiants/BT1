# [M] YesWiki: Authenticated (Admin) Server-Side Template Injection to Remote Code Execution via Bazar Semantic Templates

## Summary
Severity: Medium
Advisory: CVE-2026-52762
Aliases: GHSA-65p8-9433-jpcp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-52762
Type: osv

## Details
YesWiki is a wiki system written in PHP. Prior to version 4.6.6, YesWiki Bazar contains a stored Server-Side Template Injection (SSTI) vulnerability in the semantic template feature that can be escalated to confirmed Remote Code Execution (RCE). An authenticated administrator can place arbitrary Twig expressions into the Semantic template (Twig) field (bn_sem_template), and that content is later executed server-side when public semantic endpoints are requested. This issue has been patched in version 4.6.6.

## References
- https://github.com/YesWiki/yeswiki/releases/tag/v4.6.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52762.json
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-65p8-9433-jpcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-52762
- https://github.com/YesWiki/yeswiki/commit/89462f1577a8a1fe7fcff75e77b5058a74d8047b
