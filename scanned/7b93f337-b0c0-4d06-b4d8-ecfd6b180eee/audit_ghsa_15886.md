# [M] Minecraft MOTD Parser's HtmlGenerator vulnerable to XSS

## Summary
Severity: Medium
Advisory: GHSA-q898-frwq-f3qp
CVE: CVE-2024-47765
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-04
Source: https://github.com/advisories/GHSA-q898-frwq-f3qp
Type: github-advisory

## Affected
- Packagist: `dev-lancer/minecraft-motd-parser` — affected >=0 <1.0.6

## Details
### Summary
The `HtmlGenerator` class is subject to potential cross-site scripting (XSS) attack through a parsed malformed Minecraft server MOTD.

### Context
Minecraft server owners can set a so-called MOTD (Message of the Day) for their server that appears next to the server icon and below the server name on the multiplayer server list of a player's Minecraft client. The Minecraft server sends the MOTD in the `description` property of the [Status Response](https://wiki.vg/Server_List_Ping#Status_Response) packet. The [jgniecki/MinecraftMotdParser](https://github.com/jgniecki/MinecraftMotdParser) PHP library is able to parse the value of the `description` property, which can be either a string or an array of text components. By utilizing the aforementioned `HtmlGenerator` class, it is also able to transform the value into an HTML string that can be used to visualize the MOTD on a web page.

### Details
The `HtmlGenerator` iterates through objects of `MotdItem` that are contained in an object of `MotdItemCollection` to generate a HTML string. An attacker can make malicious inputs to the `color` and `text` properties of `MotdItem` to inject own HTML into a web page during web page generation. For example by sending a malicious MOTD from a Minecraft server under their control that was queried and passed to the `HtmlGenerator`.

This XSS vulnerability exists because the values of these properties are neither filtered nor escaped, as can be seen here:
- https://github.com/jgniecki/MinecraftMotdParser/blob/0412f68eeb91729a00444a8d6c00c45623884aa5/src/Generator/HtmlGenerator.php#L49
- https://github.com/jgniecki/MinecraftMotdParser/blob/0412f68eeb91729a00444a8d6c00c45623884aa5/src/Generator/HtmlGenerator.php#L80

### Proof of Concept
JavaScript code can be injected into the `HtmlGenerator` by parsing either a string via `TextParser` or an array via `ArrayParser`. The following code examples demonstrate the vulnerability by triggering the alert dialog of the browser.

#### XSS via `TextParser`
```php
<?php

use DevLancer\MinecraftMotdParser\Collection\MotdItemCollection;
use DevLancer\MinecraftMotdParser\Generator\HtmlGenerator;
use DevLancer\MinecraftMotdParser\Parser\TextParser;

$motdCollection = (new TextParser())->parse('<script>alert("XSS on page load")</script>', new MotdItemCollection());

echo (new HtmlGenerator())->generate($motdCollection);
```

#### XSS via `ArrayParser`
```php
<?php

use DevLancer\MinecraftMotdParser\Collection\MotdItemCollection;
use DevLancer\MinecraftMotdParser\Generator\HtmlGenerator;
use DevLancer\MinecraftMotdParser\Parser\ArrayParser;

$motdCollection = (new ArrayParser())->parse([
    [
        'color' => '#" onmouseover="javascript:alert(\'XSS when mouse pointer enters the span element\')"',
        'text' => 'Hover me',
    ],
    [
        'color' => '#000000',
        'text' => '<script>alert("XSS on page load")</script>',
    ]
], new MotdItemCollection());

echo (new HtmlGenerator())->generate($motdCollection);
```

### Impact
If the `HtmlGenerator` class of this library is used, this XSS vulnerability can potentially affect:
- Players visiting Minecraft server list websites (of which there are several dozen online, written in PHP) that display the MOTD.
- Users visiting Minecraft server status websites to query information about a Minecraft server.
- Server owners managing their Minecraft server via a web interface that displays the MOTD, where the attack could be carried out by a malicious Minecraft server plugin that modifies the MOTD without the server owner's consent.

It is not clear if and which platforms depend on this library.

### Remediation
I suggest converting all HTML special characters in the values of the `color` and `text` properties to HTML entities. The display of the HTML entities will still be correct in the browser, but the XSS vulnerability will be eliminated as the values will no longer be interpreted as HTML by the browser.

This could be achieved by introducing a new private `escape` function in the `HtmlGenerator` class:
```php
private function escape(string $text): string
{
    return htmlentities($text, ENT_QUOTES | ENT_HTML5, 'UTF-8');
}
```

This function should be called in the following two lines:
- https://github.com/jgniecki/MinecraftMotdParser/blob/0412f68eeb91729a00444a8d6c00c45623884aa5/src/Generator/HtmlGenerator.php#L49
Change to: `$tags['span'][] = sprintf('color: %s;', $this->escape($motdItem->getColor()));`
- https://github.com/jgniecki/MinecraftMotdParser/blob/0412f68eeb91729a00444a8d6c00c45623884aa5/src/Generator/HtmlGenerator.php#L80
Change to: `$value = sprintf($value, $this->escape($motdItem->getText()));`

## References
- https://github.com/jgniecki/MinecraftMotdParser/security/advisories/GHSA-q898-frwq-f3qp
- https://nvd.nist.gov/vuln/detail/CVE-2024-47765
- https://github.com/jgniecki/MinecraftMotdParser/commit/b0ab9d68a964cd3d74977f39a9e7af0a94509f7c
- https://github.com/jgniecki/MinecraftMotdParser
- https://github.com/jgniecki/MinecraftMotdParser/blob/0412f68eeb91729a00444a8d6c00c45623884aa5/src/Generator/HtmlGenerator.php#L49
- https://github.com/jgniecki/MinecraftMotdParser/blob/0412f68eeb91729a00444a8d6c00c45623884aa5/src/Generator/HtmlGenerator.php#L80
