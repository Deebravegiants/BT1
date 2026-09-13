# [M] Lemur: Missing authorization check on POST /certificates/<id>/export for plugins with requires_key = False

## Summary
Severity: Medium
Advisory: GHSA-4h97-p9wq-chqj
CVE: CVE-2026-71322
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-4h97-p9wq-chqj
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.3

## Details
## Summary
 
The `CertificateExport` handler in `lemur/certificates/views.py` nests its entire ownership / `CertificatePermission` check inside an `if plugin.requires_key:` branch. When the selected export plugin advertises `requires_key = False`, the authorization check is skipped entirely and any authenticated user can invoke `plugin.export(cert.body, cert.chain, cert.private_key, options)` against a certificate they do not own. The handler additionally writes a `"key_view"` audit-log event for every call, regardless of whether the plugin actually accessed the private key, polluting the audit trail with false positives.
 
## Root Cause
 
`lemur/certificates/views.py:1573`:
 
```python
if plugin.requires_key:
    if not cert.private_key:
        return (..., 400)
    else:
        if g.current_user != cert.user:
            owner_role = role_service.get_by_name(cert.owner)
            permission = CertificatePermission(owner_role, [x.name for x in cert.roles])
            if not permission.can():
                return (..., 403)
 
log_service.create(g.current_user, "key_view", certificate=cert)   # always logged
extension, passphrase, data = plugin.export(
    cert.body, cert.chain, cert.private_key, options
)
```
 
The authorization gate is structurally inside the `if plugin.requires_key:` block. With `requires_key = False`, control falls straight through to `plugin.export(...)` with no ownership check. The `cert.private_key` is passed to the plugin regardless of the flag — the flag only describes what the plugin *advertises* it needs, not what it actually receives.
 
The only currently shipping `ExportPlugin` with `requires_key = False` is `JavaTruststoreExportPlugin` (`lemur/plugins/lemur_jks/plugin.py`), whose `export()` ignores the `key` argument and emits a public-only Java truststore. The present-day data exposure is therefore limited to public certificate material. The bug is nonetheless filed as a real authorization gap because:
 
1. The structural defect is latent and silent - any future `requires_key = False` `ExportPlugin` that *does* read `cert.private_key` will inherit the bypass with no test or code-review signal.
2. The unconditional `log_service.create(..., "key_view", ...)` call falsely records key-view events for callers who never viewed a key, weakening incident-response signal.
 
## Affected Endpoints
 
| Method | Path | Source |
|---|---|---|
| POST | /api/1/certificates/`<id>`/export | lemur/certificates/views.py:1573 |
 
## Impact
 
In the current codebase:
 
- Any authenticated user can mint a Java truststore (`java-truststore-jks` plugin) containing any certificate's public body and chain, without owning the certificate or holding a role with permission over it.
- The audit log records a `key_view` event for the calling user against that certificate, despite no private key having been accessed. Defenders investigating apparent key-view events will encounter false positives that they cannot distinguish from genuine accesses.
 
Latent risk:
 
- A future `ExportPlugin` author who sets `requires_key = False` because their plugin can *operate* without a key (e.g., for a fall-back code path) but still uses the key when one is provided will silently leak private keys to any authenticated user. The same code review that approves the plugin will not flag this — the authorization invariant is held by a structurally distant `if`-branch in the view, not by the plugin itself.
 
## Remediation
 
Lift the authorization check out of the `if plugin.requires_key:` block so it runs for every export call:
 
```python
# Authorization first, unconditionally.
if g.current_user != cert.user:
    owner_role = role_service.get_by_name(cert.owner)
    permission = CertificatePermission(owner_role, [x.name for x in cert.roles])
    if not permission.can():
        return (dict(message="You are not authorized to export this certificate."), 403)
 
if plugin.requires_key:
    if not cert.private_key:
        return (dict(message="Plugin requires a key but none is present."), 400)
    log_service.create(g.current_user, "key_view", certificate=cert)   # only when key actually accessed
 
extension, passphrase, data = plugin.export(
    cert.body, cert.chain, cert.private_key, options
)
```
 
This makes the authorization gate independent of the plugin's `requires_key` flag and correctly scopes the `key_view` audit event to calls that actually involve key access.
 
## Steps to Reproduce
 
1. Set up Lemur with default configuration. Create an admin user `admin` and a non-admin user `eve` with the `read-only` role (or any role without certificate permissions).
 
2. As `admin`, issue a certificate. Note its `id`.
 
3. As `eve`, invoke export with the `java-truststore-jks` plugin:
````
   curl -X POST https://lemur.local/api/1/certificates/<cert_id>/export \
        -H "Authorization: Bearer <eve_jwt>" \
        -H "Content-Type: application/json" \
        -d '{
              "plugin": {
                "slug": "java-truststore-jks",
                "plugin_options": [
                  {"name": "passphrase", "value": "test"}
                ]
              }
            }'
````
 
4. Observe HTTP 200 with a base64-encoded JKS truststore in the response. `eve` had no permission over `admin`'s certificate, yet successfully exported its public material.
 
5. Inspect the audit log table or `lemur logs list`:
````
   psql lemur -c "SELECT user_id, log_type, certificate_id, logged_at FROM logs
                  WHERE certificate_id = <cert_id> ORDER BY logged_at DESC LIMIT 1;"
````
   The log row shows `log_type = 'key_view'` for `eve` against `admin`'s certificate, despite no private key actually being accessed by the truststore plugin - confirming the audit-log pollution facet of the bug.

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-4h97-p9wq-chqj
- https://github.com/Netflix/lemur/commit/5683bbea8b10cce07f9a8abf1e4a7d3b2031c585
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.3
