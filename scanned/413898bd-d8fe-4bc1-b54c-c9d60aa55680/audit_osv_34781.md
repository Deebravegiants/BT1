# [M] Rallly Has Unauthorized Poll Duplication via Insecure Direct Object Reference (IDOR)

## Summary
Severity: Medium
Advisory: CVE-2025-65020
Aliases: GHSA-44w7-pf32-gv5m
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-65020
Type: osv

## Details
Rallly is an open-source scheduling and collaboration tool. Prior to version 4.5.4, an Insecure Direct Object Reference (IDOR) vulnerability in the poll duplication endpoint (/api/trpc/polls.duplicate) allows any authenticated user to duplicate polls they do not own by modifying the pollId parameter. This effectively bypasses access control and lets unauthorized users clone private or administrative polls. This issue has been patched in version 4.5.4.

## References
- https://github.com/lukevella/rallly/releases/tag/v4.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65020.json
- https://github.com/lukevella/rallly/security/advisories/GHSA-44w7-pf32-gv5m
- https://nvd.nist.gov/vuln/detail/CVE-2025-65020
