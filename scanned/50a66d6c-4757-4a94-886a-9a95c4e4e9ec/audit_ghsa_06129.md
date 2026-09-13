# [H] Grav: Unauthenticated denial of service via unbounded image derivative dimensions

## Summary
Severity: High
Advisory: GHSA-4x9g-vw65-vvf9
CVE: CVE-2026-53653
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-14
Source: https://github.com/advisories/GHSA-4x9g-vw65-vvf9
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=2.0.0-beta.1 <2.0.0-rc.8
- Packagist: `getgrav/grav` — affected >=0 <1.7.53

## Details
### Summary
An unauthenticated visitor exhausts server memory and CPU by requesting an image with oversized resize dimensions. One request drives a worker to several gigabytes of RAM and tens of seconds of CPU. A few concurrent requests take the host down.

### Details
`Grav::fallbackUrl()` (system/src/Grav/Common/Grav.php:800-804) loops over every query parameter and, when the name matches `ImageMedium::$magic_actions`, calls that method on the medium with the comma-split value as arguments:

```php
foreach ($uri->query(null, true) as $action => $params) {
    if (in_array($action, ImageMedium::$magic_actions, true)) {
        call_user_func_array([&$medium, $action], explode(',', $params));
    }
}
```

`forceResize` runs with `force=true`, so it sets the output size to the attacker's values with no clamp against the source or any ceiling. The `getgrav/image` GD adapter then calls `imagecreatetruecolor($w, $h)`. libgd allocates that buffer outside PHP's `emalloc`, so `memory_limit` does not cap it. Grav exposes no `system.images.max_width`/`max_height` setting.

### PoC
Any page that serves an image works. With a 200x150 source image:

```
GET /home/test.png?forceResize=20000,20000
```

Measured on PHP 8.4.21 with `memory_limit=128M`:

- peak worker RSS 3,109 MB
- 21.9 s CPU
- HTTP 200, 1.6 MB response

`8000x8000` already needs ~244 MB. The cache key includes the dimensions, so varying them forces fresh work on every request.

### Impact
Unauthenticated denial of service against any Grav site that serves images. No account, plugin, or non-default config required.

## Fix
Clamp the request-derived dimensions before dispatch, behind a configurable cap. The image library is the wrong layer; bound the arguments at the request boundary.

```diff
--- a/system/src/Grav/Common/Grav.php
+++ b/system/src/Grav/Common/Grav.php
@@ public function fallbackUrl($path)
                 foreach ($uri->query(null, true) as $action => $params) {
                     if (in_array($action, ImageMedium::$magic_actions, true)) {
-                        call_user_func_array([&$medium, $action], explode(',', $params));
+                        $args = explode(',', $params);
+                        $max = (int) $config->get('system.images.max_dimension', 8000);
+                        if ($max > 0
+                            && in_array($action, ['resize', 'forceResize', 'cropResize', 'cropZoom', 'zoomCrop', 'crop'], true)) {
+                            foreach ($args as $a) {
+                                if (is_numeric($a) && (int) $a > $max) {
+                                    return false; // reject oversized derivative request
+                                }
+                            }
+                        }
+                        call_user_func_array([&$medium, $action], $args);
                     }
                 }
```

Document `system.images.max_dimension` (default 8000) so operators can tune it. A total-pixel ceiling (`width * height`) is a stricter alternative.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-4x9g-vw65-vvf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-53653
- https://github.com/getgrav/grav/commit/d9f9f0369a07ae5c96cde700c7949e1237b29cf6
- https://github.com/getgrav/grav/commit/f4c0f42eea755cedad6f626b342c88d4cba72174
- https://github.com/getgrav/grav
- https://github.com/getgrav/grav/releases/tag/1.7.53
- https://github.com/getgrav/grav/releases/tag/2.0.0-rc.8
