# [C] DQL injection through sorting parameters blocked

## Summary
Severity: Critical
Advisory: GHSA-2xmm-g482-4439
CVE: CVE-2022-24752
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-15
Source: https://github.com/advisories/GHSA-2xmm-g482-4439
Type: github-advisory

## Affected
- Packagist: `sylius/grid-bundle` — affected >=0 <1.10.1

## Details
### Impact
Values added at the end of query sorting were passed directly to the DB. We don't know, if it could lead to direct SQL injections, however, we should not allow for easy injection of values there anyway.

### Patches
The issue is fixed in version 1.10.1 and in 1.11-rc.1

### Workarounds

You have to overwrite your `Sylius\Component\Grid\Sorting\Sorter.php` class:

```php
<?php

// src/App/Sorting/Sorter.php

declare(strict_types=1);

namespace App\Sorting;

use Symfony\Component\HttpKernel\Exception\BadRequestHttpException;
use Sylius\Component\Grid\Data\DataSourceInterface;
use Sylius\Component\Grid\Definition\Grid;
use Sylius\Component\Grid\Parameters;
use Sylius\Component\Grid\Sorting\SorterInterface;

final class Sorter implements SorterInterface
{
    public function sort(DataSourceInterface $dataSource, Grid $grid, Parameters $parameters): void
    {
        $enabledFields = $grid->getFields();
        $expressionBuilder = $dataSource->getExpressionBuilder();

        $sorting = $parameters->get('sorting', $grid->getSorting());
        $this->validateSortingParams($sorting, $enabledFields);

        foreach ($sorting as $field => $order) {
            $this->validateFieldNames($field, $enabledFields);

            $gridField = $grid->getField($field);
            $property = $gridField->getSortable();

            if (null !== $property) {
                $expressionBuilder->addOrderBy($property, $order);
            }
        }
    }

    private function validateSortingParams(array $sorting, array $enabledFields): void
    {
        foreach (array_keys($enabledFields) as $key) {
            if (array_key_exists($key, $sorting) && !in_array($sorting[$key], ['asc', 'desc'])) {
                throw new BadRequestHttpException(sprintf('%s is not valid, use asc or desc instead.', $sorting[$key]));
            }
        }
    }

    private function validateFieldNames(string $fieldName, array $enabledFields): void
    {
        $enabledFieldsNames = array_keys($enabledFields);

        if (!in_array($fieldName, $enabledFieldsNames, true)) {
            throw new BadRequestHttpException(sprintf('%s is not valid field, did you mean one of these: %s?', $fieldName, implode(', ', $enabledFieldsNames)));
        }
    }
}
```
and register it in your container: 

```yaml
# config/services.yaml
services:
    # ...
    sylius.grid.sorter:
        class: App\Sorting\Sorter
```

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues)
* Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/SyliusGridBundle/security/advisories/GHSA-2xmm-g482-4439
- https://nvd.nist.gov/vuln/detail/CVE-2022-24752
- https://github.com/Sylius/SyliusGridBundle/pull/222
- https://github.com/Sylius/SyliusGridBundle/commit/73d0791d0575f955e830a3da4c3345f420d2f784
- https://github.com/Sylius/SyliusGridBundle
- https://github.com/Sylius/SyliusGridBundle/releases/tag/v1.10.1
- https://github.com/Sylius/SyliusGridBundle/releases/tag/v1.11.0-RC.2
