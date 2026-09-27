# [H] Rallly Improper Authorization Allows Reopening of Any Finalized Poll via Public pollId

## Summary
Severity: High
Advisory: CVE-2025-65034
Aliases: GHSA-5fp2-pv2j-rqpc
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-65034
Type: osv

## Details
Rallly is an open-source scheduling and collaboration tool. Prior to version 4.5.4, an improper authorization vulnerability allows any authenticated user to reopen finalized polls belonging to other users by manipulating the pollId parameter. This can disrupt events managed by other users and compromise both availability and integrity of poll data. This issue has been patched in version 4.5.4.

## References
- https://github.com/lukevella/rallly/releases/tag/v4.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65034.json
- https://github.com/lukevella/rallly/security/advisories/GHSA-5fp2-pv2j-rqpc
- https://nvd.nist.gov/vuln/detail/CVE-2025-65034
