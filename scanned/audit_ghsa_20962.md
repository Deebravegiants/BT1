# [H] NodeBB account takeover via SSO plugins

## Summary
Severity: High
Advisory: GHSA-xmgg-fx9p-prq6
CVE: CVE-2022-36076
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-xmgg-fx9p-prq6
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=0 <1.17.2

## Details
_This is a historical security advisory, pertaining to a vulnerability that was reported, patched, and published in 2021. It is listed here for completeness and for CVE tracking purposes._

### Impact
Due to an unnecessarily strict conditional in the code handling the first step of the SSO process, the pre-existing logic that added (and later checked) a nonce was inadvertently rendered opt-in instead of opt-out.

This re-exposed a vulnerability in that a specially crafted MITM attack could theoretically take over another user account during the single sign-on process.

### Patches
The issue has been fully patched as of v1.17.2.

The patch commit can be found at https://github.com/NodeBB/NodeBB/commit/a2400f6baff44cb2996487bcd0cc6e2acc74b3d4

### Workarounds
Site maintainers can cherry-pick https://github.com/NodeBB/NodeBB/commit/a2400f6baff44cb2996487bcd0cc6e2acc74b3d4 into their codebase to patch the exploit.

### References
* https://blogs.opera.com/security/2022/03/bug-bounty-adventures-a-nodebb-0-day/

### For more information
If you have any questions or comments about this advisory:
* Discuss it on [our community forum](community.nodebb.org/)
* Email us at [support@nodebb.org](mailto:support@nodebb.org)

## References
- https://github.com/NodeBB/NodeBB/security/advisories/GHSA-xmgg-fx9p-prq6
- https://nvd.nist.gov/vuln/detail/CVE-2022-36076
- https://github.com/NodeBB/NodeBB/commit/a2400f6baff44cb2996487bcd0cc6e2acc74b3d4
- https://blogs.opera.com/security/2022/03/bug-bounty-adventures-a-nodebb-0-day
- https://github.com/NodeBB/NodeBB
