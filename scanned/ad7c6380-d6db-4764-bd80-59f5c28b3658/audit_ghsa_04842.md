# [M] WWBN AVideo: Unauthenticated Reflected XSS via $_GET['search'] in AVideo YouTubeAPI Gallery Pagination

## Summary
Severity: Medium
Advisory: GHSA-hgjh-6wj8-gcgf
CVE: CVE-2026-50182
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-hgjh-6wj8-gcgf
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
# Unauthenticated Reflected XSS via `$_GET['search']` in AVideo YouTubeAPI Gallery Pagination

## Summary

A reflected Cross-Site Scripting vulnerability (CWE-79) in the AVideo YouTubeAPI plugin allows any unauthenticated attacker to execute arbitrary JavaScript in a victim's browser session when the victim follows a crafted URL. The `$_GET['search']` query parameter is concatenated directly into the `href` attribute of two pagination links in `plugin/YouTubeAPI/gallerySection.php` (lines 67 and 74) with no `htmlspecialchars`, no `urlencode`, and no allow-list check. An injected `<script>` element is then extracted by the AVideo Layout plugin and concatenated into a single trailing inline script block at the bottom of the page, where the browser executes it.

## Details

`plugin/YouTubeAPI/gallerySection.php` renders the YouTubeAPI plugin's gallery section on the AVideo homepage (and every page that includes `plugin/Gallery/view/mainArea.php`) when the API plugin is enabled with `showGallerySection=true` (the default). The pagination block at lines 67 and 74 builds the previous-page and next-page `<a>` elements by string-interpolating `$_GET['search']` directly:

```php
// plugin/YouTubeAPI/gallerySection.php:67
<a href="<?php echo "{$global['webSiteRootURL']}page/".($_GET['page']-1)."?pageToken={$object->prevPageToken}&search=".(@$_GET['search']); ?>" ...>

// plugin/YouTubeAPI/gallerySection.php:74
<a href="<?php echo "{$global['webSiteRootURL']}page/".($_GET['page']+1)."?pageToken={$object->nextPageToken}&search=".(@$_GET['search']); ?>" ...>
```

The `@` operator only suppresses an undefined-index warning; it does not sanitize the value. A payload like `"><script>alert(1337)</script>` closes the `href` attribute, closes the `<a>` element, and injects a fresh `<script>` tag.

Two preconditions gate the sink. First, the YouTube API call must return a pagination token (always true for any non-trivial result set, since the mock or real YouTube response carries `nextPageToken` for multi-page queries). Second, `plugin/Gallery/view/mainArea.php` line 53 wraps the gallery render in `if (!empty($video)) { echo AVideoPlugin::getGallerySection(); } else { /* output captured and discarded */ }`. When `$_GET['search']` is set, `Video::getVideo()` adds a MySQL fulltext `MATCH(v.title) AGAINST (<search>) IN NATURAL LANGUAGE MODE` clause; the payload tokenizes to words like `script`, `alert`, `1337`, and the gate passes whenever any video in the corpus has a title containing one of those words. Realistic deployments overwhelmingly satisfy this; the attacker can also seed the payload with a common word (`?search=video"><script>...</script>`) to guarantee a fulltext hit.

The AVideo Layout plugin (`plugin/Layout/Layout.php:611`, enabled by default) runs `Layout::organizeHTML()` over the final HTML, extracts every inline `<script[^>]*>(.*)</script>` block via regex, and concatenates their inner contents into one trailing `<script>` block placed immediately before `</body>`. The injected `<script>alert(1337)</script>` is therefore moved out of the original `href` context and into a clean executable script block; the visible pagination markup retains only the leftover `&search=">` bytes.

**Affected product:** AVideo (WWBN), API + YouTubeAPI + Layout plugins
**Tested version:** master branch, commit 122b184 (snapshot dated 2026-05-22)

## PoC

The AVideo deployment must have the YouTubeAPI plugin enabled with the default `showGallerySection=true`. The payload also needs to satisfy the fulltext `MATCH(v.title) AGAINST` gate that `Video::getVideo()` adds when `$_GET['search']` is set: at least one video in the corpus must have a title containing one of the payload's tokens. In the live confirmation a video titled `Tutorial about script error alerts` satisfied the gate via the words `script` and `alert`. Seeding the payload with the common word `video` guarantees a hit on any realistic AVideo deployment, since `video` appears in nearly every video title.

Open the following URL in any browser. No authentication, no session cookie, no prior interaction with the site is required:

```
https://avideo.example/?search=video%22%3E%3Cscript%3Ealert(1337)%3C%2Fscript%3E&page=2
```

The browser fires an `alert(1337)` modal dialog as soon as the homepage finishes rendering. The injected `<script>` is no longer inside the `href` markup at render time; it lives inside the page's single trailing inline script block, surfaced there by the Layout plugin's HTML reorganization.

## Impact

This is a Reflected XSS vulnerability (CWE-79) on the AVideo public homepage. Any unauthenticated remote attacker who induces a victim to follow a crafted URL executes arbitrary JavaScript in the victim's browser session under the AVideo origin, reading non-`HttpOnly` cookies and issuing authenticated AJAX requests as the victim. When the victim is an AVideo administrator, the injected JavaScript performs any admin action (create user, promote to admin, change configuration, install plugin) that uses cookie-based authentication without an additional CSRF token, escalating a single click on a crafted link into full administrative takeover.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-hgjh-6wj8-gcgf
- https://github.com/WWBN/AVideo/commit/f50fc033b7adb36f1ffd6640e7826468bdafdec3
- https://github.com/WWBN/AVideo
