# [H] Lemur: Unchecked `replaces[]` lets any user silence notifications and hijack auto-rotation for arbitrary certificates

## Summary
Severity: High
Advisory: GHSA-cfh6-pv5c-38jv
CVE: CVE-2026-71308
CWE: CWE-639, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-cfh6-pv5c-38jv
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0.5.0 <1.9.3

## Details
## Summary

Repo under test: https://github.com/Netflix/lemur

The certificate create and upload endpoints accept a `replaces[]` (alias `replacements`) array that is resolved to live `Certificate` ORM objects with no ownership or `CertificatePermission` check on the referenced certificates. The SQLAlchemy `Certificate.replaces` append listener then immediately sets `victim.notify = False` and populates `victim.replaced`. From that point the victim certificate is excluded from auto-reissue, its expiration notifications are silenced, and the periodic `certificate_rotate` Celery task deploys the attacker's certificate (`endpoint.certificate.replaced[0]`) onto every endpoint serving the victim certificate.

Any authenticated non-read-only user can therefore silently substitute their own certificate onto production load balancers and Kubernetes secrets they hold no role on, while suppressing the legitimate certificate's lifecycle automation.

## Affected route

`POST /api/1/certificates`
`POST /api/1/certificates/upload`
`PUT /api/1/certificates/<id>`

## Affected code

- [`lemur/certificates/schemas.py:402`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/schemas.py#L402) — `replaces = fields.Nested(AssociatedCertificateSchema, missing=[], many=True)` accepted on create/upload/edit
- [`lemur/schemas.py:152`](https://github.com/Netflix/lemur/blob/main/lemur/schemas.py#L152) — `AssociatedCertificateSchema` resolves any certificate by id/name via `fetch_objects(Certificate, data)` with no permission check
- [`lemur/certificates/views.py:651`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/views.py#L651) — only `StrictRolePermission().can()` gates `/certificates/upload`; no check on `data['replaces']`
- [`lemur/certificates/models.py:506`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/models.py#L506) — `@event.listens_for(Certificate.replaces, 'append')` sets `value.notify = False` on the victim
- [`lemur/certificates/service.py:277`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/service.py#L277) — `get_all_pending_reissue()` filters `not_(Certificate.replaced.any())`, excluding the victim
- [`lemur/certificates/cli.py:347`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/cli.py#L347) — `request_rotation(endpoint, endpoint.certificate.replaced[0], message, commit)` deploys the attacker cert
- [`lemur/common/celery.py:638`](https://github.com/Netflix/lemur/blob/main/lemur/common/celery.py#L638) — periodic `certificate_rotate` task runs `cli_certificate.rotate(..., commit=True)`
- [`lemur/deployment/service.py:17`](https://github.com/Netflix/lemur/blob/main/lemur/deployment/service.py#L17) — `endpoint.source.plugin.update_endpoint(endpoint, new_cert)` pushes to ELB/CloudFront/ACM/K8s

## Impact

An authenticated insider or holder of a stolen low-privilege token can, without holding any role on a target certificate:

1. Upload a self-signed or attacker-minted certificate listing arbitrary high-value production certificate IDs in `replaces`.
2. Immediately disable expiration notifications and auto-reissue for those production certificates.
3. On the next scheduled `certificate_rotate` Celery run, have the attacker's certificate pushed to every endpoint (AWS ELB/CloudFront/ACM, Kubernetes, SFTP, etc.) currently serving the victim certificate, while the legitimate certificate is detached.

Minimum impact is fleet-wide TLS denial of service equivalent to mass revocation. Where internal clients trust the substituted chain (or combined with the sub-CA finding LEMUR-BUG-07), it escalates to TLS interception. This directly violates the invariant that a user may only modify or revoke a certificate if they are its owner, a member of an owning role, or an administrator.

## Root cause

`AssociatedCertificateSchema.get_object` calls `fetch_objects(Certificate, data)` and returns the ORM rows verbatim. No caller on the create/upload/edit path iterates the resolved `replaces` list to enforce `CertificatePermission` before the model assigns them, and the `Certificate.replaces` append event listener mutates the victim row (`notify = False`) as a side effect of ORM collection assignment. The direct revoke endpoint *does* enforce `CertificatePermission`, but this `replaces` path achieves an equivalent or worse outcome while bypassing it entirely.

## Validated evidence

Static trace, confirmed by code inspection (validation status: `CONFIRMED`):

- `replaces` is accepted in `CertificateInputSchema` / `CertificateUploadInputSchema` and resolved via `fetch_objects(Certificate, ...)` with no per-object authorization.
- `grep -n CertificatePermission lemur/certificates/views.py` shows the check is applied to `PUT`/`DELETE`/`revoke`/`export` paths but never to the `replaces` payload of `POST /certificates` or `POST /certificates/upload`.
- The Celery `certificate_rotate` task and `cli.rotate()` consume `Endpoint.replaced.any()` unconditionally and deploy `replaced[0]` with `commit=True`.

## Proof of concept / reproducer

Status: reconstructed from source report (static control-flow trace; not executed against a live CA).

Preconditions: attacker is an authenticated Lemur user holding any role other than `read-only` (default `StrictRolePermission` config). `<VICTIM_CERT_ID>` is any certificate id readable via `GET /api/1/certificates`.

```bash
# 1. Upload an attacker-controlled cert that "replaces" the victim
curl -sS -X POST "<TARGET_BASE_URL>/api/1/certificates/upload" \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "attacker-replacement",
        "owner": "attacker@example.com",
        "body": "-----BEGIN CERTIFICATE-----\n<ATTACKER_CERT_PEM>\n-----END CERTIFICATE-----",
        "privateKey": "-----BEGIN PRIVATE KEY-----\n<ATTACKER_KEY_PEM>\n-----END PRIVATE KEY-----",
        "replaces": [{"id": <VICTIM_CERT_ID>}]
      }'

# 2. Observe victim.notify is now false and victim is queued for rotation
curl -sS "<TARGET_BASE_URL>/api/1/certificates/<VICTIM_CERT_ID>" \
  -H "Authorization: Bearer <AUTH_TOKEN>" | jq '.notify, .replaced'

# 3. On the next certificate_rotate Celery beat tick, the attacker cert is
#    deployed to every endpoint that was serving <VICTIM_CERT_ID>.
```

Static-trace validation command from the source report:

```bash
grep -n 'replaces' lemur/certificates/schemas.py lemur/certificates/views.py lemur/schemas.py \
  && grep -n 'CertificatePermission' lemur/certificates/views.py
```

Source artifact: `audit/harnesses/public-repo-threat-model-harness/results/netflix-lemur-100run-mythos-20260627T051129Z/findings.jsonl` (run_083, finding cluster `lemur-replaces-unauth`, 7/100 runs).

## Suggested fix

Before persisting `replaces`/`replacements` on certificate create, upload, and edit, iterate each referenced certificate and enforce the same `CertificatePermission(owner_role, cert.roles)` check used by the revoke endpoint ([`views.py:1677-1685`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/views.py#L1677)); reject with 403 if the caller is not creator/owner/role-member/admin for any target. Additionally, move the `value.notify = False` side effect out of the SQLAlchemy append listener so an authorization failure cannot leave a victim certificate partially mutated, and emit an `audit_log` entry whenever a certificate is marked as replaced.

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-cfh6-pv5c-38jv
- https://github.com/Netflix/lemur/commit/286874535160952143b0afe2d356642669f9d4c6
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.3
