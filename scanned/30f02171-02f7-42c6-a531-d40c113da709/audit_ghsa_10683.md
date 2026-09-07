# [M] AVideo: Unauthenticated Instagram Graph API Proxy via publishInstagram.json.php

## Summary
Severity: Medium
Advisory: GHSA-x9w5-xccw-5h9w
CVE: CVE-2026-35179
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-x9w5-xccw-5h9w
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The SocialMediaPublisher plugin exposes a `publishInstagram.json.php` endpoint that acts as an unauthenticated proxy to the Facebook/Instagram Graph API. The endpoint accepts user-controlled parameters including an access token, container ID, and Instagram account ID, and passes them directly to the Graph API via `InstagramUploader::publishMediaIfIsReady()`. This allows any unauthenticated user to make arbitrary Graph API calls through the server, potentially using stolen tokens or abusing the platform's own credentials.

## Details

At `plugin/SocialMediaPublisher/publishInstagram.json.php:14`, the endpoint passes request parameters directly to the Instagram Graph API without any authentication check:

```php
InstagramUploader::publishMediaIfIsReady(
    $_REQUEST['accessToken'],
    $_REQUEST['containerId'],
    $_REQUEST['instagramAccountId']
);
```

There is no call to `User::isLogged()`, `User::isAdmin()`, or any other authorization check before processing the request.

In contrast, sibling endpoints in the same plugin enforce proper authorization:
- `uploadVideo.json.php` requires `User::isLogged()`
- `refresh.json.php` requires `User::isAdmin()`

The endpoint was confirmed accessible on a live instance: it returns a Graph API error response, demonstrating that it processes the request and forwards it to Facebook's servers.

## Proof of Concept

1. Send a request to the endpoint without any authentication:

```bash
curl -s "https://your-avideo-instance.com/plugin/SocialMediaPublisher/publishInstagram.json.php" \
  -d "accessToken=TEST_TOKEN&containerId=TEST_CONTAINER&instagramAccountId=TEST_ACCOUNT"
```

2. The server forwards the request to the Facebook Graph API. With invalid parameters, it returns a Graph API error confirming the endpoint is functional:

```json
{
  "error": {
    "message": "Invalid OAuth access token.",
    "type": "OAuthException",
    "code": 190
  }
}
```

3. With a valid access token (e.g., one leaked from AVI-027), an attacker could publish content to the platform's Instagram account:

```bash
curl -s "https://your-avideo-instance.com/plugin/SocialMediaPublisher/publishInstagram.json.php" \
  -d "accessToken=LEAKED_ACCESS_TOKEN&containerId=REAL_CONTAINER_ID&instagramAccountId=REAL_ACCOUNT_ID"
```

4. Verify that sibling endpoints require authentication:

```bash
# Should require login
curl -s "https://your-avideo-instance.com/plugin/SocialMediaPublisher/uploadVideo.json.php"

# Should require admin
curl -s "https://your-avideo-instance.com/plugin/SocialMediaPublisher/refresh.json.php"
```

## Impact

The unauthenticated endpoint allows any attacker to use the AVideo server as a proxy for Instagram/Facebook Graph API calls. When combined with credentials leaked from AVI-027 (unauthenticated access to social media API credentials), an attacker can publish, modify, or delete content on the platform's Instagram account without any authentication to the AVideo instance. The server's IP address is used for the API calls, which could also be used to bypass rate limits or IP-based restrictions on the Graph API.

- **CWE-862**: Missing Authorization
- **Severity**: Medium

## Recommended Fix

Add an admin authorization check at the top of `plugin/SocialMediaPublisher/publishInstagram.json.php:10`, consistent with the sibling `refresh.json.php` endpoint:

```php
// plugin/SocialMediaPublisher/publishInstagram.json.php:10
if(!User::isAdmin()){
    die(json_encode(['error'=>'Not authorized']));
}
```

This restricts the endpoint to admin users only, matching the authorization level of `refresh.json.php` and preventing unauthenticated proxy abuse.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-x9w5-xccw-5h9w
- https://nvd.nist.gov/vuln/detail/CVE-2026-35179
- https://github.com/WWBN/AVideo
