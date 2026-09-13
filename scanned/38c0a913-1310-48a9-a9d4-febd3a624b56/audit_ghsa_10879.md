# [M] Firefly III user API endpoints expose all users' information to any authenticated user (IDOR)

## Summary
Severity: Medium
Advisory: GHSA-5q8v-j673-m5v4
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-5q8v-j673-m5v4
Type: github-advisory

## Affected
- Packagist: `grumpydictator/firefly-iii` — affected >=6.4.23 <6.5.1

## Details
### Summary

The User management API endpoints (`GET /api/v1/users` and `GET /api/v1/users/{id}`) are accessible to any authenticated user without admin/owner role verification, exposing all users' email addresses, roles, and account status.

### Affected Endpoints

1. **GET /api/v1/users** (UserController::index, line 94) — Lists ALL users with full details. No role check.
2. **GET /api/v1/users/{id}** (UserController::show, line 126) — Shows any user's details by ID. No role check.

### Root Cause (1-of-N Inconsistency)

Other methods in the same controller properly check for the 'owner' role:

- `store()` — `UserStoreRequest::authorize()` checks `auth()->user()->hasRole('owner')` ✓
- `destroy()` — Explicitly checks `$this->repository->hasRole($admin, 'owner')` ✓

But `index()` and `show()` have no role check at all. The route group at `routes/api.php:734-747` has no admin middleware, only the global `auth:api` middleware.

### Exposed Data

The `UserTransformer` (line 40-54) returns:
- `email` — user's email address
- `role` — user's role (owner/demo)
- `blocked` — account blocked status
- `blocked_code` — block reason
- `created_at` / `updated_at` — timestamps

### Impact

Any authenticated user can:
1. Enumerate ALL user accounts in the instance
2. Harvest email addresses for phishing/social engineering
3. Identify admin/owner accounts by role
4. Determine which accounts are blocked

### Exploitation

```bash
# List all users
curl -H "Authorization: Bearer <any_user_token>" https://instance/api/v1/users

# View specific user details
curl -H "Authorization: Bearer <any_user_token>" https://instance/api/v1/users/1
```

### Suggested Fix

Add owner role checks to `index()` and `show()`, or restrict the route group with admin middleware:

```php
// Option 1: Add check in controller methods
public function show(User $user): JsonResponse
{
    if (!$this->repository->hasRole(auth()->user(), 'owner') && auth()->user()->id !== $user->id) {
        throw new FireflyException('200025: No access to function.');
    }
    // ...
}

// Option 2: Add middleware to route group
Route::group(['middleware' => ['admin'], ...], ...)
```

## References
- https://github.com/firefly-iii/firefly-iii/security/advisories/GHSA-5q8v-j673-m5v4
- https://github.com/firefly-iii/firefly-iii
