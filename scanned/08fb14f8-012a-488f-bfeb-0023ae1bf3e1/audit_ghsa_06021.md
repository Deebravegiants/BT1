# [M] Winter: My Account preview exposes another backend user's profile by record ID

## Summary
Severity: Medium
Advisory: GHSA-mpmw-f6h6-3g26
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-mpmw-f6h6-3g26
Type: github-advisory

## Affected
- Packagist: `winter/wn-backend-module` — affected >=1.2.13 <1.2.14

## Details
### Impact

`Backend\Controllers\MyAccount`, introduced in v1.2.13, declares an empty `$requiredPermissions` array so that any authenticated backend user can manage their own account. It implements the `FormController` behavior, which exposes three routable actions — `create`, `update` and `preview` — that each take a record id from the URL.

`index()` passes the authenticated user's own id to the behavior, but the inherited actions were left routable and `formFindModelObject()` was not scoped, so a caller-supplied id resolved against an unscoped `Backend\Models\User` query:

```
GET /backend/backend/myaccount/preview/{other_user_id}
```

`preview` disclosed the target user's first name, last name, login, email address and avatar; `update` was equally routable and additionally disclosed role, group membership, superuser flag and throttle state. Password controls render a mask, so no credential material was exposed. Backend user ids are sequential and trivially enumerated, and as these are `GET` actions no CSRF token is involved.

The behavior's AJAX handlers (`create_onSave`, `update_onSave`, `update_onDelete`) were also dispatchable on these routes, but cross-user writes were blocked by the `Backend\Models\User` authorization guards added in v1.2.13. The confirmed impact is unauthorized disclosure of backend user profile data.

To actively exploit this security issue, an attacker would need access to the Backend with a user account with any level of access.

### Patches

`MyAccount` no longer exposes the generic record actions it never used as routes, and its form lookup is now pinned to the authenticated user:

- `protected $guarded = ['create', 'update', 'preview'];` removes the inherited actions from routing. The guard has to be at the routing layer, as handler dispatch (`{action}_{handler}`) runs before the page action.
- `formExtendQuery()` constrains every lookup made by the behavior to the current user's key.

This security issue has been fixed as of **v1.2.14** (commit [`cdbc8f5a23db27f72ccec658a8e5769e6d9f6dcb`](https://github.com/wintercms/winter/commit/cdbc8f5a23db27f72ccec658a8e5769e6d9f6dcb)).

### Workarounds

There is no supported workaround other than upgrading. If you cannot upgrade immediately, you may apply the fix manually in `modules/backend/controllers/MyAccount.php`:

1. Add `protected $guarded = ['create', 'update', 'preview'];` to the controller.
2. Add a `formExtendQuery()` method that scopes the lookup to the current user:

```php
public function formExtendQuery(\Winter\Storm\Database\Builder $query): void
{
    $query->whereKey($this->user->getKey());
}
```

### References

- https://github.com/wintercms/winter/security/advisories/GHSA-j5jq-cr68-v2xx
- https://github.com/wintercms/winter/commit/cdbc8f5a23db27f72ccec658a8e5769e6d9f6dcb


Credit to Awwader ([@NRAwwad](https://github.com/NRAwwad)) for reporting the issue.

### For more information

If you have any questions or comments about this advisory:
- Email us at [hello@wintercms.com](mailto:hello@wintercms.com)

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-mpmw-f6h6-3g26
- https://github.com/wintercms/winter/commit/cdbc8f5a23db27f72ccec658a8e5769e6d9f6dcb
- https://github.com/wintercms/winter
- https://github.com/wintercms/winter/releases/tag/v1.2.14
