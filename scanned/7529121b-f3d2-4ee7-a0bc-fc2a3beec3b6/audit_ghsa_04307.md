# [H] StarCitizenWiki Extension Embed Video: Stored XSS via unsanitized class passed to template

## Summary
Severity: High
Advisory: GHSA-7h5p-637f-jfr7
CVE: CVE-2026-55691
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-7h5p-637f-jfr7
Type: github-advisory

## Affected
- Packagist: `starcitizenwiki/embedvideo` — affected >=0 <4.1.0

## Details
### Summary
The user supplied class value is fed directly into the sprintf call that creates HTML. You can add a quote to escape the class and then inject arbitrary html/javascript to the final output.

### Details
The template [here](https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/a573a16d925ee0ea0d34b360856dc8ab0b88f822/includes/EmbedService/EmbedHtmlFormatter.php#L138) adds a figure with a class that is substituted in. This value is provided to sprintf [here](https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/blob/a573a16d925ee0ea0d34b360856dc8ab0b88f822/includes/EmbedService/EmbedHtmlFormatter.php#L156), an unescaped version of the class supplied by the user.

```
$template = <<<HTML
    <figure class="%s" data-service="%s" %s %s>
        <div class="embedvideo-wrapper" %s>%s%s%s</div>%s
    </figure>
HTML;
```

### PoC
Note the double quote immediately following the single quote to escape the class attribute in the template:
```
<youtube class='" onmouseover="alert(document.domain)' id="dQw4w9WgXcQ">dQw4w9WgXcQ</youtube>
```

### Impact
Arbitrary HTML can be inserted into the DOM by any user on any page, allowing for JavaScript to be executed.

## References
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/security/advisories/GHSA-7h5p-637f-jfr7
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/commit/370156335b325bb81d14d89edf0a1f2643d50a84
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo
- https://github.com/StarCitizenWiki/mediawiki-extensions-EmbedVideo/releases/tag/v4.1.0
