# [M] Wallos: Cross-user subscription cost inference via replacement_subscription_id

## Summary
Severity: Medium
Advisory: CVE-2026-50198
Aliases: GHSA-hggr-v8rm-c6jj
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-50198
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 4.9.1, an authenticated user can edit their own inactive subscription and set replacement_subscription_id to a subscription ID belonging to another user. The write is accepted, and later the stats logic dereferences that foreign subscription ID without user_id scoping. This lets the attacker infer the victim subscription's monthly-normalized cost by observing changes in their own stats output. This does not expose the full victim subscription object, but it does expose derived financial metadata. This issue has been patched in version 4.9.1.

## References
- https://github.com/ellite/Wallos/releases/tag/v4.9.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50198.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-hggr-v8rm-c6jj
- https://nvd.nist.gov/vuln/detail/CVE-2026-50198
