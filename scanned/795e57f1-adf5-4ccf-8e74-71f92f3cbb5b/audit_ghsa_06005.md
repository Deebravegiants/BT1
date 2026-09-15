# [M] Lemur: Sub-CA creation never checks `AuthorityPermission` on the parent authority

## Summary
Severity: Medium
Advisory: GHSA-g7p5-89mh-248h
CVE: CVE-2026-71317
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-g7p5-89mh-248h
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.3

## Details
## Summary

Repo under test: https://github.com/Netflix/lemur

When `ADMIN_ONLY_AUTHORITY_CREATION=False` (an explicitly supported and documented configuration), `POST /api/1/authorities` with `type=subca` never verifies that the caller holds `AuthorityPermission` on the supplied `parent` authority. The `parent` field is resolved by `AssociatedAuthoritySchema` via a raw `fetch_objects(Authority, data)` lookup, then passed straight through `service.create → mint → cryptography-issuer.create_authority`, which loads `options["parent"].authority_certificate.private_key` and signs a brand-new intermediate CA on the caller's behalf.

Any authenticated non-read-only user can therefore mint a sub-CA chained to any internal root whose private key Lemur holds — including roots they hold no role on — attach a role they already belong to, and immediately issue or offline-sign trusted leaf certificates for arbitrary names.

## Affected route

`POST /api/1/authorities` (with `type=subca`)

## Affected code

- [`lemur/authorities/views.py:231`](https://github.com/Netflix/lemur/blob/main/lemur/authorities/views.py#L231) — gates only on `AuthorityCreatorPermission()` + `StrictRolePermission()`; no `AuthorityPermission` on `data['parent']`
- [`lemur/authorities/schemas.py:58`](https://github.com/Netflix/lemur/blob/main/lemur/authorities/schemas.py#L58) — `parent = fields.Nested(AssociatedAuthoritySchema)`; `validate_subca` only checks presence
- [`lemur/schemas.py:107`](https://github.com/Netflix/lemur/blob/main/lemur/schemas.py#L107) — `AssociatedAuthoritySchema.get_object` → `fetch_objects(Authority, data)` resolves any authority by id/name with no permission check
- [`lemur/plugins/lemur_cryptography/plugin.py:40`](https://github.com/Netflix/lemur/blob/main/lemur/plugins/lemur_cryptography/plugin.py#L40) — `private_key = options["authority"].authority_certificate.private_key` (set from `options["parent"]`) signs the new intermediate
- [`lemur/auth/permissions.py:62`](https://github.com/Netflix/lemur/blob/main/lemur/auth/permissions.py#L62) — `AuthorityCreatorPermission` becomes always-allow when `ADMIN_ONLY_AUTHORITY_CREATION=False`
- [`lemur/certificates/views.py:538`](https://github.com/Netflix/lemur/blob/main/lemur/certificates/views.py#L538) — `is_private_authority` (true for `cryptography-issuer`) skips `USER_DOMAIN_AUTHORIZATION_PROVIDER` for subsequent leaf issuance

## Impact

In deployments that set `ADMIN_ONLY_AUTHORITY_CREATION=False` to enable self-service CA creation, any authenticated non-read-only user — with zero permission on a given internal root CA — can obtain a working intermediate CA chained to that root. They can then:

- Issue TLS certificates for arbitrary names trusted by every relying party that trusts the internal root, bypassing `LEMUR_ALLOWED_DOMAINS`, sensitive-domain flags, and the per-user domain-authorization plugin.
- Export the sub-CA private key and sign end-entity certificates entirely outside Lemur, defeating all in-product issuance controls.

This converts "can create a self-contained test CA" into "can mint trusted certs under any internal PKI root in the organisation". The `ADMIN_ONLY_AUTHORITY_CREATION` documentation does not warn operators of this consequence.

## Root cause

`AuthoritiesList.post` evaluates `AuthorityCreatorPermission` (a global "may create authorities" flag) and `StrictRolePermission`, but never evaluates `AuthorityPermission(parent.id, parent.roles)` against the caller-supplied `parent`. `AssociatedAuthoritySchema` is a pure lookup schema with no authz hook, and neither `authorities.service.create` nor `mint` re-check before invoking `issuer_plugin.create_authority(options)`. The bundled `cryptography-issuer` then uses the parent's stored private key directly.

## Validated evidence

Static trace, confirmed by code inspection (validation status: `CONFIRMED`):

- `parent` is loaded via `AssociatedAuthoritySchema` (raw `fetch_objects`), passed unchecked through `views.post → service.create → mint → plugin.create_authority → issue_certificate`, where the parent authority's stored private key is read and used to sign the new intermediate.
- No call to `AuthorityPermission(parent.id, ...)` exists anywhere on this path.
- Precondition `ADMIN_ONLY_AUTHORITY_CREATION=False` is an explicitly supported config ([`docs/administration.rst:517`](https://github.com/Netflix/lemur/blob/main/docs/administration.rst#L517)).

## Proof of concept / reproducer

Status: reconstructed from source report (static control-flow trace; not executed against a live CA).

Preconditions: `ADMIN_ONLY_AUTHORITY_CREATION=False`; attacker is an authenticated Lemur user holding any role other than `read-only`; `<PARENT_AUTHORITY_ID>` is any internal `cryptography-issuer` root CA the attacker holds no role on; `<ATTACKER_ROLE>` is any role the attacker already belongs to.

```bash
curl -sS -X POST "<TARGET_BASE_URL>/api/1/authorities" \
  -H "Authorization: Bearer <AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "attacker-subca",
        "owner": "attacker@example.com",
        "description": "poc",
        "type": "subca",
        "parent": {"id": <PARENT_AUTHORITY_ID>},
        "plugin": {"slug": "cryptography-issuer"},
        "roles": [{"name": "<ATTACKER_ROLE>"}],
        "commonName": "attacker-intermediate",
        "validityYears": 1
      }'
```

The response contains a new authority whose `authority_certificate` is signed by `<PARENT_AUTHORITY_ID>`'s private key. The caller is recorded as creator and holds `<ATTACKER_ROLE>` on it, so `POST /api/1/certificates` against the new authority succeeds (and skips `allowed_issuance_for_domain` because `is_private_authority` is true).

Static-trace validation command from the source report:

```bash
grep -n 'parent' lemur/authorities/schemas.py lemur/authorities/views.py lemur/authorities/service.py \
  && sed -n '37,55p' lemur/plugins/lemur_cryptography/plugin.py
```

Source artifact: `audit/harnesses/public-repo-threat-model-harness/results/netflix-lemur-100run-mythos-20260627T051129Z/findings.jsonl` (run_022, finding cluster `lemur-subca-parent-authz`, 5/100 runs).

## Suggested fix

In `AuthoritiesList.post` (or `authorities.service.create`), when `data.get('parent')` is present, enforce `AuthorityPermission(parent.id, [r.name for r in parent.roles]).can()` before invoking the issuer plugin, regardless of `ADMIN_ONLY_AUTHORITY_CREATION`. Additionally, update the `ADMIN_ONLY_AUTHORITY_CREATION` documentation to state that disabling it currently grants every authenticated user the ability to chain sub-CAs off any internal root whose private key Lemur holds. Consider also requiring admin (or an explicit per-parent capability) for any `type=subca` creation independent of the global flag.

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-g7p5-89mh-248h
- https://github.com/Netflix/lemur/commit/8669011203ca3dd89d9e39bab9ef6850eca723f9
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.3
