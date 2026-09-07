# [H] Star Citizen  EmbedVideo Extension Stored XSS through wikitext caused by usage of non-reserved data attributes

## Summary
Severity: High
Advisory: GHSA-4j5h-mvj3-m48v
CVE: CVE-2025-59839
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-4j5h-mvj3-m48v
Type: github-advisory

## Affected
- Packagist: `starcitizenwiki/embedvideo` — affected >=0

## Details
### Summary
The EmbedVideo extension allows adding arbitrary attributes to an HTML element, allowing for stored XSS through wikitext.

### Details

The attributes of an iframe are populated with the value of an unreserved data attribute (`data-iframeconfig`) that can be set via wikitext:
https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/440fb331a84b2050f4cc084c1d31d58a1d1c202d/resources/ext.embedVideo.videolink.js#L5-L20
Similar code is also present here:
https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/440fb331a84b2050f4cc084c1d31d58a1d1c202d/resources/modules/iframe.js#L139-L155

It is possible to execute JS through attributes like `onload` or `onmouseenter`.

### PoC

1. Create a page with the following contents:
```html
<div class="embedvideo-evl" data-iframeconfig='{"onload": "alert(1)"}'>Click me!</div>
<evlplayer></evlplayer>
```
2. Click on the "Click me!" text
3. Click on the "Load video" button below
<img width="855" height="404" alt="image" src="https://github.com/user-attachments/assets/afb3839a-012c-4e90-a208-a6137b704ccd" />


### Impact
Arbitrary HTML can be inserted into the DOM by any user, allowing for JavaScript to be executed.

## References
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/security/advisories/GHSA-4j5h-mvj3-m48v
- https://nvd.nist.gov/vuln/detail/CVE-2025-59839
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/commit/4e075d3dc9a15a3ee53f449a684d5ab847e52f01
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/440fb331a84b2050f4cc084c1d31d58a1d1c202d/resources/ext.embedVideo.videolink.js#L5-L20
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/440fb331a84b2050f4cc084c1d31d58a1d1c202d/resources/modules/iframe.js#L139-L155
