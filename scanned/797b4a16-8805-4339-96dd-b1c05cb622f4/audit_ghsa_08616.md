# [M] phpMyFAQ: Path Traversal in Client::deleteClientFolder enables arbitrary directory deletion by non-super-admin admins

## Summary
Severity: Medium
Advisory: GHSA-gh9p-q46p-57g2
CVE: CVE-2026-45008
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-gh9p-q46p-57g2
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.2
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.2

## Details
## Summary

`Client::deleteClientFolder()` in `phpmyfaq/src/phpMyFAQ/Instance/Client.php:583` takes a URL from the caller, strips the `https://` prefix, and passes the remainder to `Filesystem::deleteDirectory()` relative to the multisite `clientFolder`. No path-traversal validation runs. An admin with the `INSTANCE_DELETE` permission (a role short of SUPER_ADMIN) submits `https://../../../<path>` as the client URL and the server recursively deletes arbitrary directories under the web user's rights. Same pattern and reachability as GHSA-38m8-xrfj-v38x, which the project accepted at High severity three weeks earlier.

## Details

`phpmyfaq/src/phpMyFAQ/Instance/Client.php:583-591`:

```php
public function deleteClientFolder(string $sourceUrl): bool
{
    if (!$this->isMultiSiteWriteable()) {
        return false;
    }

    $sourcePath = str_replace(search: 'https://', replace: '', subject: $sourceUrl);
    return $this->filesystem->deleteDirectory($this->clientFolder . $sourcePath);
}
```

`str_replace` strips the scheme but does nothing about `../` segments. The concatenation `$this->clientFolder . $sourcePath` directly feeds the filesystem call, which traverses above `clientFolder` without complaint.

Callers feed the URL from the HTTP request body:

`phpmyfaq/src/phpMyFAQ/Controller/Administration/Api/InstanceController.php:184`:

```php
if (1 !== $instanceId && $client->deleteClientFolder($clientData->url) && $client->delete($instanceId)) {
```

`$clientData->url` comes from `json_decode($request->getContent())`. The route is `admin.api.instance.delete`, gated by `INSTANCE_DELETE`. The controller does not validate the URL against a scheme list or canonicalize the path before handing it to `deleteClientFolder()`.

`InstanceController.php:144` (edit path) and `Controller/Administration/InstanceController.php:151` (form path) both reach the same sink through different entry points.

### Precedent

GHSA-38m8-xrfj-v38x (2026-03-31) disclosed the identical bug class in `MediaBrowserController::index()`: an admin-gated API endpoint concatenates a user-supplied filename to a base directory without traversal validation. phpMyFAQ accepted that report at High severity. The present finding is the same root cause in a different controller; the project's INSTANCE_ADD / INSTANCE_DELETE permission is a granular admin right, not SUPER_ADMIN, so a lower-tier admin can reach the sink.

## Proof of Concept

Prerequisites: a phpMyFAQ 4.2.x instance with the multisite subsystem bootstrapped (there must be a non-primary instance present for the delete controller branch to fire). Alice is an admin with `INSTANCE_ADD` and `INSTANCE_DELETE` rights, no `SUPER_ADMIN` flag.

Step 1: Alice authenticates and retrieves the CSRF token for the instance admin page.

Step 2: Alice creates an instance whose `url` encodes a traversal payload. The create path at `InstanceController.php:144` already concatenates to the clientFolder through the same `deleteClientFolder(`'https://' . $hostname`)` call:

```bash
curl -sS -b "$ALICE_COOKIE" -X POST "$BASE/admin/api/instance" \
  -H "Content-Type: application/json" -H "x-csrf-token: $CSRF" \
  -d '{"url":"https://../../../tmp/pmf-poc/","instance":"poc","comment":"poc","email":"a@b","admin":"alice","password":"poc1234!"}'
```

Step 3: Alice deletes the instance. The request body names the instance id to delete; the controller hands `clientData->url` directly to `deleteClientFolder`:

```bash
curl -sS -b "$ALICE_COOKIE" -X POST "$BASE/admin/api/instance/2" \
  -H "Content-Type: application/json" -H "x-csrf-token: $CSRF" \
  -d '{"url":"https://../../../tmp/pmf-poc/"}'
```

The server computes `$sourcePath = '../../../tmp/pmf-poc/'`, concatenates to `<clientFolder>/`, and recursively deletes the resulting path.

Live verification was not attempted against the test instance because the INSTANCE_DELETE path requires the multisite/ subsystem to be bootstrapped with at least one non-primary instance; see `InstanceController.php:184`. The code path is unambiguous and the precedent GHSA confirmed the same admin gating was considered in-scope.

## Impact

Any phpMyFAQ admin holding `INSTANCE_ADD` + `INSTANCE_DELETE` but not SUPER_ADMIN can delete arbitrary directories writable by the PHP process. Outcomes:

- Destroy other tenants' data on a shared multisite deployment by traversing above the `clientFolder` into peer directories.
- Delete phpMyFAQ's own `content/`, `config/`, or cache directories and lock the install out.
- On a hosted deployment, overwrite or delete files anywhere under the web user's reach, including customer uploads outside phpMyFAQ.

phpMyFAQ's permission model gives `INSTANCE_ADD` / `INSTANCE_DELETE` as a role that a hosting operator may delegate to a subordinate admin without granting SUPER_ADMIN. That delegation is now a direct path-traversal-delete primitive.

## Recommended Fix

Canonicalize and validate the URL before forming the filesystem path.

`phpmyfaq/src/phpMyFAQ/Instance/Client.php:583`:

```php
public function deleteClientFolder(string $sourceUrl): bool
{
    if (!$this->isMultiSiteWriteable()) {
        return false;
    }

    $parsed = parse_url($sourceUrl);
    if (!is_array($parsed) || !isset($parsed['host']) || ($parsed['scheme'] ?? '') !== 'https') {
        return false;
    }

    $host = $parsed['host'];
    if (!preg_match('/^[a-z0-9][a-z0-9.-]*$/i', $host)) {
        return false;
    }

    $target = realpath($this->clientFolder . $host);
    $root = realpath($this->clientFolder);
    if ($target === false || $root === false || !str_starts_with($target, $root . DIRECTORY_SEPARATOR)) {
        return false;
    }

    return $this->filesystem->deleteDirectory($target);
}
```

`parse_url` rejects malformed inputs, the regex pins the host to valid DNS characters (no `/`, no `..`), and the `realpath` check ensures the resolved target lives under `clientFolder`. Apply the same canonicalization at the controller layer (`InstanceController::add`, `::update`, `::delete`) so the URL is validated before every call that touches the filesystem.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-gh9p-q46p-57g2
- https://nvd.nist.gov/vuln/detail/CVE-2026-45008
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-path-traversal-in-client-deleteclientfolder-via-url-parameter
