# [H] Snipe-IT vulnerable to cross-company asset maintenance re-parenting via API update

## Summary
Severity: High
Advisory: GHSA-575r-357h-fhch
CVE: CVE-2026-55516
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-575r-357h-fhch
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
The API endpoint for updating asset maintenance records allows an authorized user to change the asset_id of an existing maintenance record to an asset outside their company scope.

In a Full Multiple Company Support / multi-company deployment, this allows a user from Company A to attach or move a maintenance record onto an asset belonging to Company B. The endpoint appears to authorize access to the existing maintenance record’s asset, but does not re-authorize the newly supplied asset_id before saving the update.

###  Affected endpoint
`PATCH /api/v1/maintenances/{maintenance_id}`

Also likely affected:

`PUT /api/v1/maintenances/{maintenance_id}`

### Preconditions
The attacker needs:
- A valid authenticated API token.
- Permission to update asset maintenance records.
- Access to a maintenance record currently attached to an asset in their own company.

The attacker does not need access to the target asset’s company.

### Root cause
In the API maintenance update flow, the application checks access to the current maintenance record / current asset, then accepts attacker-controlled fields including `asset_id`.

The vulnerable behavior is that the new asset_id is not checked against the current user’s company scope before being saved.

### Relevant code path:
`app/Http/Controllers/Api/MaintenancesController.php`

The update method loads the maintenance, checks access to the existing $maintenance->asset, then calls:
```php
$maintenance->fill($request->all());
$maintenance->save();
```

Since `asset_id` is fillable on the maintenance model, the attacker can re-parent the record to another company’s asset.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### Security impact
This breaks tenant/company isolation in multi-company deployments. A scoped user can write maintenance records against assets outside their authorized company boundary.

Potential impact includes:
- Cross-company asset history pollution.
- Unauthorized modification of another company’s asset maintenance timeline.
- Incorrect maintenance, cost, audit, and warranty records on victim-company assets.
- Loss of integrity in asset lifecycle records.

This is not intended functionality because the application’s company-scoping model should prevent users from writing records onto inaccessible assets.

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-575r-357h-fhch
- https://nvd.nist.gov/vuln/detail/CVE-2026-55516
- https://github.com/grokability/snipe-it/commit/905d498ecdb0ee5591231c97bf48435e92044368
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
