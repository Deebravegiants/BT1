# [M] Gitea: Token scope bypass on web archive download endpoint

## Summary
Severity: Medium
Advisory: GHSA-cr4g-f395-h25h
CVE: CVE-2026-20706
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-cr4g-f395-h25h
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.2

## Details
## Summary

PR #37698 added checkDownloadTokenScope to /raw/*, /media/*, and attachment download web endpoints. The /archive/* endpoint (repo.Download in routers/web/repo/repo.go:372) was not included in the fix. This endpoint accepts OAuth2 tokens via webAuth.AllowOAuth2 (registered at routers/web/web.go:1649-1652) but does not call checkDownloadTokenScope or CheckRepoScopedToken.

A personal access token with any non-repository scope (e.g., read:issue or read:misc) can download full repository archives (zip/tar.gz) of private repositories the token owner has access to.

## Impact

Scope escalation: tokens scoped to non-repository categories can access full repository content through the archive download endpoint. Higher impact than endpoints fixed in #37698 because /archive/* serves the entire repository.

## Steps to Reproduce

1. Create a personal access token with ONLY read:misc scope
2. Access: GET /{owner}/{private-repo}/archive/main.tar.gz
3. Archive is served (200 OK) instead of being rejected (403 Forbidden)

Compare with fixed endpoints:
- GET /{owner}/{private-repo}/raw/branch/main/README.md correctly returns 403

## Root Cause

Download function in routers/web/repo/repo.go:372 does not call checkDownloadTokenScope. The outer group middleware reqUnitCodeReader checks repository permission but not token scope.

The API equivalent (/api/v1/repos/{owner}/{repo}/archive/*) IS properly scoped via tokenRequiresScopes(AccessTokenScopeCategoryRepository). The git HTTP endpoints are scoped via CheckRepoScopedToken in httpBase.

## Suggested Fix

Add checkDownloadTokenScope(ctx) to Download and InitiateDownload in routers/web/repo/repo.go. The function already exists in routers/web/repo/download.go (same package).

## Discovery Method

Variant analysis of PR #37698 — reviewed all web routes with webAuth.AllowOAuth2 middleware.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-cr4g-f395-h25h
- https://github.com/go-gitea/gitea
