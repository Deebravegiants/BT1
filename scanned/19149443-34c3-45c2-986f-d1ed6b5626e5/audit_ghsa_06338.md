# [M] Snipe-IT: Maintenance Record Disclosure via Missing Authorization on GET

## Summary
Severity: Medium
Advisory: GHSA-r9r3-g9fp-3q4q
CVE: CVE-2026-55703
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-r9r3-g9fp-3q4q
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.3

## Details
### Impact
Any activated account in a company can read every maintenance record for that company (asset tag, supplier, purchase cost, free-text notes, dates) without holding any asset or maintenance permission.

## Summary

`MaintenancesController::show()` renders a maintenance record without any authorization check. Every other action in the controller authorizes against the asset; `show()` does not. Any user in the asset's company can read maintenance detail (asset tag, supplier, purchase cost, notes, dates) by visiting `/maintenances/{id}`, regardless of permissions.

## Details

```php
public function show(Maintenance $maintenance): View|RedirectResponse
{
    return view('maintenances.view')->with('maintenance', $maintenance);
}
```

No `authorize()` call. The sibling actions all gate on the asset: `index()` calls `authorize('view', Asset::class)` (line 33), and `edit()`/`update()`/`destroy()` call `authorize('update', $maintenance->asset)` (lines 139, 166, 286). The route is registered with only the auth guard:

```php
Route::resource('maintenances', MaintenancesController::class, ['middleware' => ['auth']]);
```

(`routes/web/hardware.php:185`). Route-model binding still applies the company scope, so the read is bounded to the caller's company; the absent permission gate is the defect. Maintenance IDs are sequential and visible in the record URL.

## Proof of concept

1. As an administrator, create an asset in a company (here, `CompanyA`). Open the asset, choose Maintenances > Create, and add a record: name `MntA2`, supplier `SupA`, a purchase cost, and notes. The saved record opens at `/maintenances/{id}`.
2. As the administrator, create a test user assigned to CompanyA, with **every permission left unchecked**. Activate the account.
3. In a separate browser session, log in as the test user. Confirm it is unprivileged: the Assets and Maintenances navigation items are absent, and browsing to `/hardware` returns 403.
4. In the address bar, browse to `http://<host>/maintenances/{id}`.

Observed: the maintenance view renders in full for the unprivileged account.

```
GET /maintenances/5      ->  HTTP 200 OK
Renders the "Maintenance" detail page for MntA2:
  Asset: AssetA   Supplier: SupA   Cost: <value>   Notes: <text>   Dates: <...>

GET /hardware            ->  HTTP 403  (same account, asset list is gated)
GET /maintenances        ->  HTTP 403  (same account, maintenance list is gated)
GET /maintenances/2      ->  HTTP 302  (record in CompanyB; company scope still hides it)
```

- The `test` account holds zero permissions and still reads the record.
- Only the unguarded `show` route leaks: the list view and the asset pages return 403 for the same account.
- A maintenance in a different company (CompanyB) redirects away, confirming the FMCS company scope still holds.

### Patches
Patched in https://github.com/grokability/snipe-it/commit/69c50aa2aee25f837626556b4f4f3d05ec7ace96

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-r9r3-g9fp-3q4q
- https://github.com/grokability/snipe-it/commit/69c50aa2aee25f837626556b4f4f3d05ec7ace96
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.3
