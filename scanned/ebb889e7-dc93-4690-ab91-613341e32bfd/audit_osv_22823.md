# [M] Ree6 may bypass webhook protection

## Summary
Severity: Medium
Advisory: CVE-2022-39302
Aliases: GHSA-v574-xgcf-5w8x
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-10-13
Source: https://osv.dev/vulnerability/CVE-2022-39302
Type: osv

## Details
Ree6 is a moderation bot. This vulnerability would allow other server owners to create configurations such as "Better-Audit-Logging" which contain a channel from another server as a target. This would mean you could send log messages to another Guild channel and bypass raid and webhook protections. A specifically crafted log message could allow spamming and mass advertisements. This issue has been patched in version 1.9.9. There are currently no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39302.json
- https://github.com/Ree6-Applications/Ree6/security/advisories/GHSA-v574-xgcf-5w8x
- https://nvd.nist.gov/vuln/detail/CVE-2022-39302
- https://github.com/Ree6-Applications/Ree6/commit/459b5bc24f0ea27e50031f563373926e94b9aa0a
