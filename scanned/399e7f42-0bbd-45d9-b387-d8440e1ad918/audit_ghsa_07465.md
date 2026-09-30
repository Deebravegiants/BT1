# [H] Craft CMS: Authorship spoofing in `entries/save-entry` via pre-check/post-mutation authorization gap

## Summary
Severity: High
Advisory: GHSA-qq2c-2q8j-jh27
CVE: CVE-2026-50279
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-qq2c-2q8j-jh27
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.21

## Details
### Summary

`EntriesController::actionSaveEntry()` performs entry-edit permission checks before request-controlled author changes are applied to the model. The subsequent author mutation path accepts attacker-supplied `authors` / `author` parameters and allows the change when the current user is one of the old authors. Because the controller does not re-run authorization after mutating the author list, a low-privileged user can reassign an entry’s authorship to another user without holding the dedicated peer-author-change permission.

### Details
The control flow begins in [EntriesController.php](/D:/files/projects/cms-5.9.19/cms-5.9.19/src/controllers/EntriesController.php):249. `actionSaveEntry()` loads the entry and enforces edit permissions before calling `_populateEntryModel()`:

```php
public function actionSaveEntry(bool $duplicate = false): ?Response
{
    ...
    $entry = $this->_editableEntry($this->request->getBodyParam('entryId'), $siteId);
    ...
    $this->enforceEditEntryPermissions($entry, $duplicate);
    ...
    $this->_populateEntryModel($entry);
    ...
    $success = Craft::$app->getElements()->saveElement($entry);
}
```

The attacker-controlled source is in [EntriesController.php](/D:/files/projects/cms-5.9.19/cms-5.9.19/src/controllers/EntriesController.php):588:

```php
$entry->setAttributesFromRequest(array_filter([
    'authorIds' => $this->request->getBodyParam('authors') ??
        $this->request->getBodyParam('author') ??
        $entry->getAuthorId() ??
        static::currentUser()->id,
]));
```

`Entry::setAttributesFromRequest()` in [Entry.php](/D:/files/projects/cms-5.9.19/cms-5.9.19/src/elements/Entry.php):1124 extracts the new author IDs and applies them if `canChangeAuthor()` returns true:

```php
if (
    ($authorIds !== null || $authorId !== null) &&
    $this->canChangeAuthor()
) {
    $this->_oldAuthorIds = $oldAuthorIds;
    $this->setAuthorIds($authorIds);
}
```

`canChangeAuthor()` at [Entry.php](/D:/files/projects/cms-5.9.19/cms-5.9.19/src/elements/Entry.php):2789 allows the author change when the current user can view peer entries and is already one of the existing authors:

```php
return (
    empty($authorIds) ||
    in_array($user->id, $authorIds) ||
    $user->can("changeAuthorForPeerEntries:$section->uid")
);
```

After the author list is mutated, the controller does not re-check authorization. 

This closes the exploit chain:

1. External source: authenticated request to `entries/save-entry` with attacker-controlled `authors[]`.
2. Trust boundary failure: authorization is checked on the pre-mutation entry state, not on the post-mutation author assignment.
3. Privileged sink: the author relationship is rewritten in persistent storage.

Preconditions derived from the source:

1. The attacker is authenticated and can edit entry `345`.
2. The attacker is among the existing authors of entry `345`, or otherwise satisfies `canChangeAuthor()` through the old author set.
3. The attacker has `viewPeerEntries` for the section.
4. User ID `1` exists and can be assigned as an author in that section.

Result:

1. `enforceEditEntryPermissions()` succeeds on the original entry state.
2. `_populateEntryModel()` reads `authors[]=1` from the request body.
3. `setAttributesFromRequest()` updates `authorIds` because `canChangeAuthor()` is evaluated against the old authorship state.
4. `saveElement()` persists the change and `_saveAuthors()` rewrites the entry-author relation.
5. Entry `345` now appears authored by user `1`.

### Impact

This allows low-privileged users to falsify content ownership and alter the authorship of entries without having the dedicated author-management permission. The impact includes corrupted audit trails, misleading notifications, broken approval workflows, and unauthorized reassignment of content responsibility.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-qq2c-2q8j-jh27
- https://nvd.nist.gov/vuln/detail/CVE-2026-50279
- https://github.com/craftcms/cms/commit/9cc493be8b414d7116c7f2bc2a6d0926e73f1248
- https://github.com/craftcms/cms
