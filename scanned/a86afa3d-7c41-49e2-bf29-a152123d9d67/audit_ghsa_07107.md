# [H] oras-go blob upload vulnerable to credential forwarding via unvalidated Location header

## Summary
Severity: High
Advisory: GHSA-jxpm-75mh-9fp7
CVE: CVE-2026-50151
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-jxpm-75mh-9fp7
Type: github-advisory

## Affected
- Go: `oras.land/oras-go/v2` — affected >=0 <2.6.1

## Details
## Summary

oras-go follows a registry-controlled `Location` header during the monolithic blob upload flow and reuses the `Authorization` header from the initial `POST` request for the subsequent `PUT` request. If a malicious registry returns a cross-host `Location`, oras-go can send the caller's credentials to an attacker-controlled endpoint.

## Affected Versions

tested: v2.6.0 (commit 03243809936cce826494b5506f724c6dc11115b1, as-of 2026-01-24)
range: unknown; likely affects earlier v2.x releases that include the same upload flow

## Impact

Credential leak to an attacker-controlled endpoint and client-side ssrf to a cross-host target.

## Affected Component

- `registry/remote/repository.go:878-916` (`blobStore.completePushAfterInitialPost`)

## Reproduction

Attachments include `poc.zip` with a local-only harness (no real registry required). It runs a fake registry server that returns a cross-host `Location` and a second server that records whether it received `Authorization`.

```bash
unzip -q -o poc.zip -d /tmp/poc
cd /tmp/poc/poc-F-ORAS-LOCATION-UPLOAD-001
make canonical
make control
```

## Recommended Fix

- validate `Location` before uploading (scheme + hostname + effective port) against the original request, or require an explicit opt-in allowlist for cross-host upload urls
- never forward `Authorization` when the upload target changes host or scheme

## references

- security policy: https://github.com/oras-project/oras-go/security/policy
- vulnerable code: `registry/remote/repository.go` (see `blobStore.completePushAfterInitialPost`)

## References
- https://github.com/oras-project/oras-go/security/advisories/GHSA-jxpm-75mh-9fp7
- https://github.com/oras-project/oras-go/pull/1152
- https://github.com/oras-project/oras-go/commit/4683c46ef078091544f5f55fd25102f002806991
- https://github.com/oras-project/oras-go
- https://github.com/oras-project/oras-go/releases/tag/v2.6.1
