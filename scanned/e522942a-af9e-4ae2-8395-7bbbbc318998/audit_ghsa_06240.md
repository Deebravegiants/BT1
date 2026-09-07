# [H] Lemur: Any user can revoke arbitrary certificates at the CA by uploading a duplicate record and revoking it

## Summary
Severity: High
Advisory: GHSA-pxmc-2ffp-8j67
CVE: CVE-2026-71417
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-pxmc-2ffp-8j67
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.3

## Details
## Summary

Repo under test: https://github.com/Netflix/lemur

`PUT /api/1/certificates/<id>/revoke` authorizes the caller against the *Lemur database row* (creator == current user, or `CertificatePermission` over the row's roles) rather than the underlying CA-side certificate identity. Separately, `POST /api/1/certificates/upload` lets any user passing `StrictRolePermission` create a new `Certificate` row while freely supplying `body`, `authority` (resolved by id/name with no `AuthorityPermission` check) and `external_id`; there is no uniqueness constraint on `body`, `serial`, or `external_id`.

An attacker can therefore read a target certificate's public `body`, `authority.id`, and `external_id` via `GET /certificates/<id>`, upload a duplicate row, and revoke that duplicate. The creator-bypass skips `CertificatePermission`, the empty-endpoints check passes because the duplicate has none, and `service.revoke()` then revokes at the CA using the attacker-supplied `body` (ACME) or `external_id` (DigiCert/Entrust/Google CA/CFSSL) under the authority's stored CA credentials — revoking the real production certificate.

## Affected route

`POST /api/1/certificates/upload` → `PUT /api/1/certificates/<dup_id>/revoke`

## Affected code

- [`lemur/certificates/views.py:651`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/views.py#L651) — only `StrictRolePermission().can()` gates upload; no `AuthorityPermission` check
- [`lemur/certificates/schemas.py:391`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/schemas.py#L391) — `CertificateUploadInputSchema` accepts caller-supplied `authority` and `external_id`
- [`lemur/schemas.py:107`](https://github.com/Netflix/lemur/blob/main/lemur/schemas.py#L107) — `AssociatedAuthoritySchema` resolves any authority by id/name with no permission check
- [`lemur/certificates/service.py:489`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/service.py#L489) — `upload()` binds the caller-supplied authority onto the new row
- [`lemur/certificates/models.py:119`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/models.py#L119) — only `name` is unique; `body`/`serial`/`external_id` are not, and `get_or_increase_name()` auto-suffixes on collision
- [`lemur/certificates/views.py:1677`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/views.py#L1677) — `if g.current_user != cert.user: ... CertificatePermission ...` — creator of the duplicate row bypasses the owner check
- [`lemur/certificates/views.py:1687`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/views.py#L1687) — `if cert.endpoints: ...` — duplicate row has no endpoints, so the deployed-cert safeguard is bypassed
- [`lemur/certificates/service.py:1120`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/service.py#L1120) — `plugin = plugins.get(certificate.authority.plugin_name); plugin.revoke_certificate(certificate, reason)`
- [`lemur/plugins/lemur_acme/acme_handlers.py:268`](https://github.com/Netflix/lemur/blob/main/lemur/plugins/lemur_acme/acme_handlers.py#L268) — ACME revokes by `certificate.body`
- [`lemur/plugins/lemur_digicert/plugin.py:477`](https://github.com/Netflix/lemur/blob/main/lemur/plugins/lemur_digicert/plugin.py#L477), [`lemur/plugins/lemur_entrust/plugin.py:321`](https://github.com/Netflix/lemur/blob/main/lemur/plugins/lemur_entrust/plugin.py#L321) — commercial CAs revoke by `certificate.external_id`
- [`lemur/certificates/schemas.py:290`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/schemas.py#L290) — `CertificateOutputSchema` exposes `external_id`, `body`, `authority` to any authenticated user

## Impact

A low-privileged authenticated insider (or holder of a stolen non-admin token/API key) can revoke any certificate managed by Lemur — including high-value certificates they do not own and certificates currently attached to live endpoints — directly at the issuing CA. Iterating over `GET /certificates` yields fleet-wide revocation (mass DoS of TLS endpoints) without ever passing an `AuthorityPermission` or `CertificatePermission` check on the victim certificate. This is exactly the "Revocation as DoS vector" scenario flagged in the threat model and additionally defeats the built-in "cannot revoke while attached to endpoint" safeguard.

## Root cause

Revocation authority is bound to ownership of the Lemur DB row, not to the CA-side certificate identity. Because upload allows creating a second row that aliases the same CA-side certificate (same `body` / `external_id` / `authority`) without any uniqueness constraint or `AuthorityPermission` check, the attacker can manufacture a row they own and then exercise the creator-bypass on revoke. The endpoint-attached guard inspects only the duplicate row's `cert.endpoints`, which is empty.

## Validated evidence

Static path trace, confirmed by code inspection (validation status: `CONFIRMED`):

- Upload is gated only by `StrictRolePermission` (default-open to any non-read-only user) and accepts attacker-chosen `authority` + `external_id` + `body` without an `AuthorityPermission` check.
- `Certificate.body` / `external_id` have no uniqueness constraint, so a duplicate row is created.
- The revoke endpoint short-circuits the owner check when caller is the row creator, and the endpoint-attached guard inspects only the duplicate row.
- Issuer plugins revoke at the CA using `body` / `external_id` taken from the duplicate row under the authority's stored CA credentials.

## Proof of concept / reproducer

Status: reconstructed from source report (static control-flow trace; not executed against a live CA — revoking at a real CA is destructive).

Preconditions: attacker is an authenticated Lemur user holding any role other than `read-only`. `<VICTIM_CERT_ID>` is any certificate id readable via `GET /api/1/certificates`.

```bash
# 1. Read the victim's body / authority / external_id (exposed to any authenticated user)
curl -sS "<TARGET_BASE_URL>/api/1/certificates/<VICTIM_CERT_ID>" \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  | jq '{body, external_id, authority: .authority.id}'

# 2. Upload a duplicate row aliasing the same CA-side certificate
curl -sS -X POST "<TARGET_BASE_URL>/api/1/certificates/upload" \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "victim-dup",
        "owner": "attacker@example.com",
        "body": "<VICTIM_BODY_PEM>",
        "authority": {"id": <VICTIM_AUTHORITY_ID>},
        "externalId": "<VICTIM_EXTERNAL_ID>"
      }'
# → returns {"id": <DUP_ID>, ...}; attacker is now cert.user of <DUP_ID>

# 3. Revoke the duplicate — issuer plugin revokes at the CA by body/external_id
curl -sS -X PUT "<TARGET_BASE_URL>/api/1/certificates/<DUP_ID>/revoke" \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"crlReason": "unspecified"}'
```

Static-trace validation command from the source report:

```bash
grep -n 'StrictRolePermission' lemur/certificates/views.py | grep -v Authority
grep -n 'cert.authority = kwargs.get' lemur/certificates/service.py
grep -n 'g.current_user != cert.user' lemur/certificates/views.py
grep -n 'certificate.external_id\|certificate.body' \
  lemur/plugins/lemur_acme/acme_handlers.py \
  lemur/plugins/lemur_digicert/plugin.py \
  lemur/plugins/lemur_entrust/plugin.py
```

Source artifact: `audit/harnesses/public-repo-threat-model-harness/results/netflix-lemur-100run-mythos-20260627T051129Z/findings.jsonl` (run_050, finding cluster `lemur-revoke-via-duplicate`, 2/100 runs).

## Suggested fix

Decouple CA-side revocation authority from Lemur row ownership:

1. On `POST /certificates/upload`, if `authority` is supplied enforce `AuthorityPermission` for that authority, and reject/ignore caller-supplied `external_id`.
2. Before calling `plugin.revoke_certificate`, look up all `Certificate` rows sharing the same `(authority_id, serial)` or `body` and require `CertificatePermission` on every match (and run the endpoint-attached check against all matches).
3. Consider a DB uniqueness constraint or dedup on `(authority_id, serial)` so a second row for the same CA-issued certificate cannot be created.
4. Stop exposing `external_id` in `CertificateOutputSchema` to non-owners.

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-pxmc-2ffp-8j67
- https://github.com/Netflix/lemur/commit/851389ae737a6d6bf16c1f9ca64a2ce56c1cc5c6
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.3
