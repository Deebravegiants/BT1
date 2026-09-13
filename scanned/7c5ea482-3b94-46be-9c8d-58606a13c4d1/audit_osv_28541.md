# [M] CMSaasStarter: JWT Token Not Verified on Server Session

## Summary
Severity: Medium
Advisory: CVE-2024-34354
Aliases: GHSA-qgcj-9rxf-rw7q
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-34354
Type: osv

## Details
CMSaaSStarter is a SaaS template/boilerplate built with SvelteKit, Tailwind, and Supabase. Any forks of the CMSaaSStarter template before commit 7904d416d2c72ec75f42fbf51e9e64fa74062ee6 are impacted. The issue is the user JWT Token is not verified on server session. You should take the patch 7904d416d2c72ec75f42fbf51e9e64fa74062ee6 into your fork.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34354.json
- https://github.com/CriticalMoments/CMSaasStarter/security/advisories/GHSA-qgcj-9rxf-rw7q
- https://nvd.nist.gov/vuln/detail/CVE-2024-34354
- https://github.com/CriticalMoments/CMSaasStarter/commit/7904d416d2c72ec75f42fbf51e9e64fa74062ee6
- https://github.com/CriticalMoments/CMSaasStarter/pull/65
