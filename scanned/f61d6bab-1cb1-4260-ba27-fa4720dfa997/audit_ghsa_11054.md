# [H] AVideo Affected by Stored XSS via Unescaped Video Title in CDN downloadButtons.php

## Summary
Severity: High
Advisory: GHSA-gc3m-4mcr-h3pv
CVE: CVE-2026-33295
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-gc3m-4mcr-h3pv
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

WWBN/AVideo contains a stored cross-site scripting vulnerability in the CDN plugin's download buttons component. The `clean_title` field of a video record is interpolated directly into a JavaScript string literal without any escaping, allowing an attacker who can create or modify a video to inject arbitrary JavaScript that executes in the browser of any user who visits the affected download page.

### Details

At line 59 of the affected file, the following PHP code constructs a JavaScript function call:

```php
downloadURLOrAlertError(url, {}, '<?php echo $video['clean_title']; ?>.' + format, progress);
```

The `clean_title` value is echoed verbatim inside a single-quoted JavaScript string literal. No JavaScript-context escaping is applied, such as wrapping with `json_encode` or htmlspecialchars with appropriate flags. Because the value sits inside a JS string delimited by single quotes, any input containing a single quote character allows an attacker to terminate the string prematurely and inject arbitrary JavaScript expressions. The `clean_title` field is derived from user-supplied video title input, meaning any user with video creation or editing privileges can craft a malicious title. The injected script executes in the security context of whatever user loads the download page for that video, which may include administrators or authenticated users with elevated privileges.

### PoC

```python
import requests

target = "https://example.com"
login_url = f"{target}/user"
upload_url = f"{target}/video/addNew"

session = requests.Session()

session.post(login_url, data={
    "user[user]": "attacker",
    "user[pass]": "attackerpassword"
})

malicious_title = "');alert(document.cookie);//"

session.post(upload_url, data={
    "title": malicious_title,
    "description": "poc"
})
```

After the video is created, navigate to:

```
https://example.com/plugin/CDN/downloadButtons.php?videos_id=<TARGET_VIDEO_ID>
```

The rendered page will contain:

```javascript
downloadURLOrAlertError(url, {}, '');alert(document.cookie);//.' + format, progress);
```

### Impact

Any user who can create or edit a video can store malicious JavaScript that will execute in the browser of any other user who visits the download page for that video. This includes scenarios where an attacker with a low-privilege account targets administrator sessions. Successful exploitation enables session cookie theft, credential harvesting, and actions performed on behalf of the victim within the application. Because the payload is stored server-side and triggers without further attacker interaction, all users who access download pages for attacker-controlled videos are at risk.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-gc3m-4mcr-h3pv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33295
- https://github.com/WWBN/AVideo/commit/30cdd825fa5778c1d678c2402be2413b84ee4833
- https://github.com/WWBN/AVideo
