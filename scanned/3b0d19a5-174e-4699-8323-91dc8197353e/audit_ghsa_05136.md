# [M] phpMyFAQ: Missing userHasPermission() in 4 API write endpoints (CVE-2026-24421 Incomplete Fix)

## Summary
Severity: Medium
Advisory: GHSA-8c6h-7g6x-m5x4
CVE: CVE-2026-49205
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-8c6h-7g6x-m5x4
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.4
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.4

## Details
Missing Authorization in API CategoryController —  CVE-2026-24421 fixed BackupController by adding userHasPermission(PermissionType::BACKUP). The same fix was NOT applied to 4 other write endpoints in the public API.  All 4 only call hasValidToken() (shared API key) but never call userHasPermission(), allowing any API token holder to perform admin operations regardless of their user permissions.

## Summary

CVE-2026-24421 fixed BackupController by adding: $this->userHasPermission(PermissionType::BACKUP);

The same fix was NOT applied to 4 other write endpoints in the public API. All 4 only call $this->hasValidToken() — which checks a shared API key header, NOT the individual user's role permissions.

## Affected Endpoints

1. src/phpMyFAQ/Controller/Api/CategoryController.php → create()  POST /api/v4.0/category
Missing: userHasPermission(PermissionType::CATEGORY_ADD)
Any API token holder can create categories regardless of user role.

2. src/phpMyFAQ/Controller/Api/FaqController.php → create()  POST /api/v4.0/faq
   Missing: userHasPermission(PermissionType::FAQ_ADD)
   Any API token holder can create FAQ entries regardless of user role.

3. src/phpMyFAQ/Controller/Api/FaqController.php → update()  PUT /api/v4.0/faq
   Missing: userHasPermission(PermissionType::FAQ_EDIT)
   Any API token holder can update any FAQ entry regardless of user role.

4. src/phpMyFAQ/Controller/Api/QuestionController.php → create() POST /api/v4.0/question
   Missing: permission check
   Any API token holder can create questions regardless of user role.

## Root Cause

All 4 methods only call:
    $this->hasValidToken();   ← shared API key, not per-user

The fixed BackupController correctly calls:
    $this->userHasPermission(PermissionType::BACKUP);  

PermissionType::CATEGORY_ADD, FAQ_ADD, FAQ_EDIT all exist in src/phpMyFAQ/Enums/PermissionType.php — they just are not being used.

## Fix

Add userHasPermission() before the logic in each method:

    // CategoryController.create()
    $this->userHasPermission(PermissionType::CATEGORY_ADD);

    // FaqController.create()
    $this->userHasPermission(PermissionType::FAQ_ADD);

    // FaqController.update()
    $this->userHasPermission(PermissionType::FAQ_EDIT);

## Reporter

CONTACT
Santhoshini Ganta
Github:@santhoshinipayload
Email: santhoshinive75@gmail.com
LinkedIn: http://linkedin.com/in/santhoshini-g-1440621ba

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-8c6h-7g6x-m5x4
- https://nvd.nist.gov/vuln/detail/CVE-2026-49205
- https://github.com/thorsten/phpMyFAQ/commit/d5c195b1ecf5dc30fb825d7eb50d22481c24cb07
- https://github.com/thorsten/phpMyFAQ
