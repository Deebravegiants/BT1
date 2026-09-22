# [H] Pimcore: Missing Authorization in WebDAV MOVE via unchecked asset move handling

## Summary
Severity: High
Advisory: GHSA-wc7j-g8wx-m2qx
CVE: CVE-2026-45260
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-wc7j-g8wx-m2qx
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=12.0.0-RC1 <12.3.7
- Packagist: `pimcore/pimcore` — affected >=2026.1.0 <2026.1.3
- Packagist: `pimcore/pimcore` — affected >=0 <11.5.17

## Details
### Summary
Pimcore's WebDAV asset endpoint exposes a `MOVE` operation through `/asset/webdav{path}` without adding an authentication plugin in the WebDAV controller. The `Tree::move()` implementation then performs asset mutation and deletion before checking a current Pimcore user or any asset permissions.

An unauthenticated remote attacker who knows two existing asset paths in the same directory can send a WebDAV `MOVE` request that deletes the source asset. Authenticated low-privileged users may also be able to perform unauthorized asset move or overwrite operations because the move path does not enforce `rename`, `delete`, `create`, or `publish` permissions.

### Details
The route for WebDAV is globally registered and accepts arbitrary trailing paths:

```yaml
# bundles/CoreBundle/config/routing.yaml
pimcore_webdav:
    path: /asset/webdav{path}
    defaults: { _controller: Pimcore\Bundle\CoreBundle\Controller\WebDavController::webdavAction }
    requirements:
        path: '.*'
```

The controller constructs a SabreDAV server but only attaches lock and browser plugins. It does not attach an authentication plugin or perform an explicit user/session check before starting the server:

```php
# bundles/CoreBundle/src/Controller/WebDavController.php
$publicDir = new Asset\WebDAV\Folder($homeDir);
$objectTree = new Asset\WebDAV\Tree($publicDir);
$server = new \Sabre\DAV\Server($objectTree);
$server->setBaseUri($this->generateUrl('pimcore_webdav', ['path' => '/']));
$server->addPlugin($lockPlugin);
$server->addPlugin(new \Sabre\DAV\Browser\Plugin());
$server->start();
```

Most WebDAV file and folder operations perform permission checks through `isAllowed()`, but `Tree::move()` does not. In the overwrite path for a same-directory move, it deletes the source asset before resolving the current user:

```php
# models/Asset/WebDAV/Tree.php
if (dirname($sourcePath) == dirname($destinationPath)) {
    if ($asset = Asset::getByPath('/' . $destinationPath)) {
        $sourceAsset = Asset::getByPath('/' . $sourcePath);
        $asset->setData($sourceAsset->getData());
        $sourceAsset->delete();
    }
    ...
}

$user = \Pimcore\Tool\Admin::getCurrentUser();
$asset->setUserModification($user->getId());
$asset->save();
```

`Asset::delete()` removes the asset without an internal permission gate:

```php
# models/Asset.php
public function delete(bool $isNested = false): void
{
    ...
    $this->getDao()->delete();
    ...
    $this->deletePhysicalFile();
}
```

Because the source asset deletion happens before `$user->getId()`, an unauthenticated request can still cause a deletion even if later execution fails when no current user is present.

### PoC
Prerequisites:

- Pimcore 2026.1.0 with the built-in WebDAV route enabled.
- Two existing asset paths in the same directory, for example `/products/source.jpg` and `/products/existing.jpg`.
- No valid session is required for the unauthenticated deletion path.

PoC request:

```http
MOVE /asset/webdav/products/source.jpg HTTP/1.1
Host: target.example
Destination: http://target.example/asset/webdav/products/existing.jpg
Overwrite: T
```

Result:

The server will return an error after the deletion because `Tree::move()` later attempts to call `$user->getId()` when no current user exists. However, the source asset at `/products/source.jpg` has already been deleted by `$sourceAsset->delete()` before that failure point.

For an authenticated low-privileged backend user without sufficient asset permissions, the same request can also reach the unchecked move path and may overwrite the destination asset or move an asset without the expected per-asset permission checks.

### Impact
This issue allows remote unauthorized destruction of assets when paths are known or guessable. In Pimcore deployments where assets represent product images, documents, media, or DAM-managed business content, deletion or unauthorized overwrite can cause data loss, content integrity loss, and service disruption.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-wc7j-g8wx-m2qx
- https://github.com/pimcore/pimcore/pull/19120
- https://github.com/pimcore/pimcore/commit/9d7c77fd9b19fa011ce470de95d4438e65007d99
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/releases/tag/v12.3.7
