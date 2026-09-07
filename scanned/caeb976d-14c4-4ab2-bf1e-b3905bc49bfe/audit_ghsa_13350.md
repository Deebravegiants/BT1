# [M] XML External Entity (XXE) vulnerability in the XML data handler

## Summary
Severity: Medium
Advisory: GHSA-q386-w6fg-gmgp
CVE: CVE-2023-38490
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-q386-w6fg-gmgp
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <3.5.8.3
- Packagist: `getkirby/cms` — affected >=3.6.0 <3.6.6.3
- Packagist: `getkirby/cms` — affected >=3.7.0 <3.7.5.2
- Packagist: `getkirby/cms` — affected >=3.8.0 <3.8.4.1
- Packagist: `getkirby/cms` — affected >=3.9.0 <3.9.6

## Details
### TL;DR

This vulnerability only affects Kirby sites that use the `Xml` data handler (e.g. `Data::decode($string, 'xml')`) or the `Xml::parse()` method in site or plugin code. The Kirby core does not use any of the affected methods.

If you use an affected method and cannot rule out XML input controlled by an attacker, we strongly recommend to update to a patch release.

----

### Introduction

XML External Entities (XXE) is a little used feature in the XML markup language that allows to include data from external files in an XML structure. If the name of the external file can be controlled by an attacker, this becomes a vulnerability that can be abused for various system impacts like the disclosure of internal or confidential data that is stored on the server (arbitrary file disclosure) or to perform network requests on behalf of the server (server-side request forgery, SSRF).

### Impact

Kirby's `Xml::parse()` method used PHP's `LIBXML_NOENT` constant, which enabled the processing of XML external entities during the parsing operation.

The `Xml::parse()` method is used in the `Xml` data handler (e.g. `Data::decode($string, 'xml')`).

Both the vulnerable method and the data handler are not used in the Kirby core. However they may be used in site or plugin code, e.g. to parse RSS feeds or other XML files. If those files are of an external origin (e.g. uploaded by a user or retrieved from an external URL), attackers may be able to include an external entity in the XML file that will then be processed in the parsing process.

Kirby sites that don't use XML parsing in site or plugin code are *not* affected.

### Patches

The problem has been patched in [Kirby 3.5.8.3](https://github.com/getkirby/kirby/releases/tag/3.5.8.3), [Kirby 3.6.6.3](https://github.com/getkirby/kirby/releases/tag/3.6.6.3), [Kirby 3.7.5.2](https://github.com/getkirby/kirby/releases/tag/3.7.5.2), [Kirby 3.8.4.1](https://github.com/getkirby/kirby/releases/tag/3.8.4.1) and [Kirby 3.9.6](https://github.com/getkirby/kirby/releases/tag/3.9.6). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have removed the `LIBXML_NOENT` constant as processing of external entities is out of scope of the parsing logic. This protects all uses of the method against the described vulnerability.

### Credits

Thanks to Alexandre Zanni (@noraj) at [ACCEIS](https://www.acceis.fr/) and Patrick Falb (@dapatrese) at [FORMER 03](https://former03.de/) for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-q386-w6fg-gmgp
- https://nvd.nist.gov/vuln/detail/CVE-2023-38490
- https://github.com/getkirby/kirby/commit/277b05662d2b67386f0a0f18323cf68b30e86387
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.5.8.3
- https://github.com/getkirby/kirby/releases/tag/3.6.6.3
- https://github.com/getkirby/kirby/releases/tag/3.7.5.2
- https://github.com/getkirby/kirby/releases/tag/3.8.4.1
- https://github.com/getkirby/kirby/releases/tag/3.9.6
