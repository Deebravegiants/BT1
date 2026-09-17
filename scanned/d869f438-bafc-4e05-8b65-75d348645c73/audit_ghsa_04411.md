# [M] WWBN AVideo: Stored XSS via Hostile YouTube Video Title in AVideo YouTubeAPI Gallery Section

## Summary
Severity: Medium
Advisory: GHSA-66q5-cj5g-wrfx
CVE: CVE-2026-50183
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-66q5-cj5g-wrfx
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
# Stored XSS via Hostile YouTube Video Title in AVideo YouTubeAPI Gallery Section

## Summary

A stored Cross-Site Scripting vulnerability (CWE-79; chained CWE-829, Inclusion of Functionality from Untrusted Control Sphere) in the AVideo YouTubeAPI plugin renders the `snippet.title` field returned by the YouTube Data API into the homepage gallery markup with no HTML encoding. The title is set by the YouTube video uploader (anyone in the world) and is treated by AVideo as trusted content. A YouTube uploader who controls a video matching the operator's configured query injects HTML into the AVideo homepage by setting their video's title to a JavaScript-bearing string; the payload then executes in the browser of every visitor who loads any page that renders the gallery.

## Details

`plugin/YouTubeAPI/YouTubeAPI.php::listVideos()` fetches search results from the YouTube Data API and stores the `snippet.title` field unchanged inside a `YPTvideoObject`:

```php
// plugin/YouTubeAPI/YouTubeAPI.php (listVideos excerpt)
$searchResponse = $youtube->search->listSearch(
    'snippet,contentDetails,statistics', $options
);
foreach ($searchResponse['items'] as $searchResult) {
    $vid = new YPTvideoObject(
        $searchResult["id"]["videoId"],
        $searchResult['snippet']["title"],          // uploader-controlled
        $searchResult['snippet']["description"],
        $searchResult['snippet']["thumbnails"]["high"]["url"],
        $searchResult['snippet']["channelTitle"],
        "https://www.youtube.com/embed/{$searchResult['id']['videoId']}"
    );
    $object->videos[] = $vid;
}
```

`plugin/YouTubeAPI/gallerySection.php` then renders the title into three HTML contexts inside each gallery card. Four reflection sites total, three of them completely unprotected:

```php
// plugin/YouTubeAPI/gallerySection.php (foreach body)
$youtubeTitle = $video->title;
...
<a class="evideo" href="<?php echo $youtubeEmbedLink; ?>" title="<?php echo $youtubeTitle; ?>">          <!-- (i) attribute -->
    <img src="<?php echo $youtubeThumbs; ?>" alt="<?php echo str_replace('"', '', $youtubeTitle); ?>" ... />  <!-- (ii) attribute, partial -->
</a>
<a class="h6 evideo" href="<?php echo $youtubeEmbedLink; ?>" title="<?php echo $youtubeTitle; ?>">       <!-- (iii) attribute -->
    <h2><?php echo $youtubeTitle; ?></h2>                                                              <!-- (iv) element body -->
</a>
```

Sites (i), (iii), and (iv) call no encoder. Site (ii) applies `str_replace('"', '', $youtubeTitle)` which strips quotes from one attribute and leaves the other three reflections untouched. The strongest sink is (iv) at line 60: a title containing `<script>alert(2222)</script>` produces `<h2><script>alert(2222)</script></h2>` in the rendered DOM, which the browser parses as a live script element and executes synchronously. The single half-mitigation at line 57 is the maintainer's evidence of awareness of the attribute-injection risk; the same developer left the other three sinks unprotected.

AVideo additionally caches the YouTube response for `cacheTimeout` seconds (default 3600), so even after the title is changed on YouTube or the video is removed, the AVideo gallery continues to serve the malicious title until the cache expires or is manually flushed.

**Affected product:** AVideo (WWBN), YouTubeAPI plugin
**Tested version:** master branch, commit 122b184 (snapshot dated 2026-05-22)

## PoC

The AVideo operator must have the YouTubeAPI plugin enabled (the default after configuring a YouTube Data API key) with `showGallerySection=true` (the default). The attacker controls a YouTube video (uploaded under any free YouTube account) whose title is set to:

```
<script>alert(2222)</script>
```

The attacker arranges for the AVideo operator's configured YouTube search query (the `keyword` plugin setting, typically a channel name or topical phrase) to match the hostile video. The matching condition is the same as a normal YouTube search: a unique phrase in the video's description, a channel name the operator follows, or any query the operator has configured.

After AVideo's `cacheTimeout` window elapses (default 3600 seconds) and a fresh `listVideos()` call fetches the malicious title, any visitor opening the AVideo homepage triggers an `alert(2222)` modal dialog as the gallery card renders.

For deterministic test reproduction, deploy a mock YouTube Data API service that impersonates `www.googleapis.com` and `youtube.googleapis.com` on the AVideo Docker network and returns the malicious title directly. The PoC then reduces to:

```
https://avideo.example/
```

Configure the YouTubeAPI plugin in the admin panel (`/plugins`) with any non-empty `developer_key` and any `keyword` value, then load the homepage. The browser fires `alert(2222)` as the gallery section finishes rendering.

## Impact

This is a Stored XSS vulnerability (CWE-79) in a publicly-rendered HTML context, with the data source under attacker control (CWE-829). Every visitor who loads any AVideo page rendering the YouTubeAPI gallery section is impacted: the injected JavaScript runs in the visitor's session under the AVideo origin, reads non-`HttpOnly` cookies, and issues authenticated requests as the visitor. When the visitor is an AVideo administrator, the injected JavaScript performs any admin action (create user, promote to admin, change configuration, install plugin) that uses cookie-based authentication without an additional CSRF token, escalating the bug into full administrative takeover. The payload persists for the duration of `cacheTimeout` (default 3600 seconds) after the malicious title is set on YouTube and survives YouTube removing the hostile video for the same window.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-66q5-cj5g-wrfx
- https://github.com/WWBN/AVideo/commit/7292129eaee5f609beae103b5cb387d55f17b877
- https://github.com/WWBN/AVideo
