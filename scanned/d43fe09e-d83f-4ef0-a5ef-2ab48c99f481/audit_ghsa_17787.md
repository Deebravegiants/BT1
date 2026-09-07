# [H] PHP-Textile has persistent XSS vulnerability in image link handling

## Summary
Severity: High
Advisory: GHSA-95m2-chm4-mq7m
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-01-07
Source: https://github.com/advisories/GHSA-95m2-chm4-mq7m
Type: github-advisory

## Affected
- Packagist: `netcarver/textile` — affected >=0 <4.1.3

## Details
### Details

Persistent XSS vulnerability in image link handling of PHP-Textile versions 4.1.2 and older, when running the parser in restricted mode. In restricted mode it is expected that the input would be sanitized, allowing user-input (such as user comments) to be parsed and handled safely by the PHP-Textile library.

In restricted mode, the version 4.1.2 of the library does not sanitize or validate user-controllable href input in image links, but allows any link protocol or JavaScriptt links to be used. The vulnerability allows an attacker to add malicious JavaScript code to the page which is then executed when an unexpecting user clicks the link.

In non-restricted mode, the library allows mixed HTML input, and any link protocol by design. In restricted mode, text links were already handled correctly and the vulnerability only affects image links.

### Resolution

This issue was fixed in PHP-Textile version 4.1.3. Version 4.1.3 disallows use of JavaScript in image links when the parser is ran in restricted mode. Restricted mode can be enabled with `Parser::setRestricted()` method prior to calling the `parse` method. For more information, see **Parsing unstructed input** in the project's [README](https://github.com/textile/php-textile?tab=readme-ov-file#parsing-untrusted-input).

### PoC

The following Textile input:

```
!securing.pl(Click Tu)!:javascript:document.innerHTML='<script>alert(1);</script>'+document.cookie)
```

Would render as the following HTML even in restricted mode:

`<p><a href="javascript:document.innerHTML=&#39;&lt;script&gt;alert(1);&lt;/script&gt;&#39;+document.cookie"><img alt="Click Tu" src="securing.pl" title="Click Tu"></a>)</p>`

### Impact

The attacker can perform any operation in the application with user’s privileges or remotely control user’s browser with automated tools.

## References
- https://github.com/textile/php-textile/security/advisories/GHSA-95m2-chm4-mq7m
- https://github.com/textile/php-textile/commit/ab18ae9703bee8b15f1b9d889d40e1881728bae6
- https://github.com/textile/php-textile
