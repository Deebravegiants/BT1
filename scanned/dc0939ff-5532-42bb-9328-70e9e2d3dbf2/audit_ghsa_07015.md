# [H] Craft CMS's mass assignment via id in newAttributes during bulk duplicate overwrites existing elements

## Summary
Severity: High
Advisory: GHSA-x5m4-g2cq-52pq
CVE: CVE-2026-50281
CWE: CWE-915
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-x5m4-g2cq-52pq
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.7.0 <5.9.21

## Details
## Summary

There is a mass-assignment flaw in the bulk-duplicate element action. Alice, holding only the permission to duplicate an entry she owns, submits an arbitrary `id` through the `newAttributes` request parameter. The duplication routine overrides its own `id = null` reset with that value and writes Alice’s attributes into Bob’s existing entry row.

## Details

`ElementsController::beforeAction()` (`src/controllers/ElementsController.php:119-124`) pulls the request body into `$this->_attributes` and rejects requests that ship an `id` or `canonicalId` key at the top level:

```php
$this->_attributes = $this->request->getBodyParams();

// No funny business
if (isset($this->_attributes['id']) || isset($this->_attributes['canonicalId'])) {
    throw new BadRequestHttpException('Changing an element’s ID is not allowed.');
}
```

The check inspects only the top-level payload. `actionBulkDuplicate()` (`src/controllers/ElementsController.php:1708-1749`) reads a separate `newAttributes` array and passes it straight through to the service layer:

```php
$elementInfo = $this->request->getRequiredBodyParam('elements');
$newAttributes = $this->request->getRequiredBodyParam('newAttributes');
...
$safeNewAttributes = Collection::make($newAttributes)
    ->only($element->safeAttributes())
    ->all();
...
$newElement = $elementsService->duplicateElement(
    $element,
    $safeNewAttributes + $element::baseBulkDuplicateAttributes(),
    false,
    checkAuthorization: true,
);
```

`Elements::duplicateElement()` (`src/services/Elements.php:1814-1840`) clones the source element, sets `id` to null, and then hands the attacker's array to `Craft::configure()`:

```php
$mainClone = clone $element;
$mainClone->id = null;
$mainClone->uid = StringHelper::UUID();
...
Craft::configure($mainClone, ArrayHelper::merge(
    $newAttributes,
    $siteAttributes[$mainClone->siteId] ?? [],
));
```

`Craft::configure()` overwrites the reset `id` with any numeric value inside `$newAttributes`. Yii's `saveElement()` then performs an UPDATE against the row with that primary key instead of an INSERT. Alice's title, slug, authorId, postDate, and UID land on Bob’s entry.

`safeAttributes()` on `Entry` includes `id` because the base element model exposes it, so the `Collection::only()` filter does not strip it.

## Impact

A low-privileged author overwrites any other element (entries, categories, users that share the Entry element table inheritance) by predicting or enumerating element IDs. Content integrity on the entire install breaks. The attack requires only the ability to duplicate one entry Alice already owns.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-x5m4-g2cq-52pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-50281
- https://github.com/craftcms/cms/commit/8f6587c25050bbb6e080d59c71f6bb8932fc8600
- https://github.com/craftcms/cms
