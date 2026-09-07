# [H] StarCitizenWiki Extension Embed Video: Stored XSS via unsanitized service name in exception text

## Summary
Severity: High
Advisory: GHSA-c29q-5xm7-5p62
CVE: CVE-2026-55690
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-c29q-5xm7-5p62
Type: github-advisory

## Affected
- Packagist: `starcitizenwiki/embedvideo` — affected >=0 <4.1.0

## Details
### Summary
When passing an unknown service name to embedvideo, an error message is rendered containing the invalid service name. The service name is not sanitized and can contain HTML.

### Details
There is a hardcoded list of allowed services in a switch statement inside `EmbedServiceFactory#newFromName` [here](https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/a573a16d925ee0ea0d34b360856dc8ab0b88f822/includes/EmbedService/EmbedServiceFactory.php#L105). When the service name is not known, an exception is thrown with the service name injected into the message via sprintf [here](https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/a573a16d925ee0ea0d34b360856dc8ab0b88f822/includes/EmbedService/EmbedServiceFactory.php#L286). This message is not sanitized and is marked as isHtml [here](https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/a573a16d925ee0ea0d34b360856dc8ab0b88f822/includes/EmbedVideo.php#L303-L311). Similarly with `{{evl:` [here](https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/a573a16d925ee0ea0d34b360856dc8ab0b88f822/includes/EmbedVideo.php#L177-L183).

### PoC
```
// Must be on a page, not on ExpandTemplates
{{#ev:<img src=x onerror=alert(document.domain)>|dQw4w9WgXcQ}}
{{#evl:id=dummy|service=<img src=x onerror=alert(document.domain)>}}
```

### Impact
Stored XSS that allows arbitrary Javascript/HTML insertion on any page that a user can edit.  It requires no interaction and executes in the wiki origin for every visitor to the page.

## References
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/security/advisories/GHSA-c29q-5xm7-5p62
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/commit/9215564bf28a0ceb40be550a55ab78efc0accc56
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/releases/tag/v4.1.0
