# [M] Gitea Stopwatch API Missing Authorization Check Leads to Post-Revocation Information Disclosure

## Summary
Severity: Medium
Advisory: BIT-gitea-2026-20883
Aliases: CVE-2026-20883, GHSA-644v-xv3j-xgqg, GHSA-j8xr-c56q-m8jj, GO-2026-4368
Ecosystem: Bitnami
Published: 2026-01-30
Source: https://osv.dev/vulnerability/BIT-gitea-2026-20883
Type: osv

## Affected
- Bitnami: `gitea` — affected >=0 <1.25.4

## Details
Gitea's stopwatch API does not re-validate repository access permissions. After a user's access to a private repository is revoked, they may still view issue titles and repository names through previously started stopwatches.

## References
- https://blog.gitea.com/release-of-1.25.4/
- https://github.com/go-gitea/gitea/pull/36340
- https://github.com/go-gitea/gitea/pull/36368
- https://github.com/go-gitea/gitea/releases/tag/v1.25.4
- https://github.com/go-gitea/gitea/security/advisories/GHSA-644v-xv3j-xgqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-20883
