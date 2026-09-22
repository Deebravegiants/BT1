# [H] Field injection in the KirbyData text storage handler

## Summary
Severity: High
Advisory: GHSA-x5mr-p6v4-wp93
CVE: CVE-2023-38488
CWE: CWE-140, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-x5mr-p6v4-wp93
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <3.5.8.3
- Packagist: `getkirby/cms` — affected >=3.6.0 <3.6.6.3
- Packagist: `getkirby/cms` — affected >=3.7.0 <3.7.5.2
- Packagist: `getkirby/cms` — affected >=3.8.0 <3.8.4.1
- Packagist: `getkirby/cms` — affected >=3.9.0 <3.9.6

## Details
### TL;DR

This vulnerability affects all Kirby sites that might have potential attackers in the group of authenticated Panel users or that allow external visitors to update a Kirby content file (e.g. via a contact or comment form).

Your Kirby sites are *not* affected if they don't allow write access for untrusted users or visitors.

----

### Introduction

A field injection in a content storage implementation is a type of vulnerability that allows attackers with content write access to overwrite content fields that the site developer didn't intend to be modified.

In a Kirby site this can be used to alter site content, break site behavior or inject malicious data or code. The exact security risk depends on the field type and usage.

### Impact

Kirby stores content of the site, of pages, files and users in text files by default. The text files use Kirby's KirbyData format where each field is separated by newlines and a line with four dashes (`----`).

When reading a KirbyData file, the affected code first removed the Unicode BOM sequence from the file contents and afterwards split the content into fields by the field separator.

When writing to a KirbyData file, field separators in field data are escaped to prevent user input from interfering with the field structure. However this escaping could be tricked by including a Unicode BOM sequence in a field separator (e.g. `--\xEF\xBB\xBF--`). When writing, this was not detected as a separator, but during the read process the BOM was removed, turning the malicious line into a valid separator. This could be abused by attackers to inject other field data into content files.

Because each field can only be defined once per content file, this vulnerability only affects fields in the content file that were defined above the vulnerable user-writable field or not at all. Fields that are defined below the vulnerable field override the injected field content and were therefore already protected.

### Patches

The problem has been patched in [Kirby 3.5.8.3](https://github.com/getkirby/kirby/releases/tag/3.5.8.3), [Kirby 3.6.6.3](https://github.com/getkirby/kirby/releases/tag/3.6.6.3), [Kirby 3.7.5.2](https://github.com/getkirby/kirby/releases/tag/3.7.5.2), [Kirby 3.8.4.1](https://github.com/getkirby/kirby/releases/tag/3.8.4.1) and [Kirby 3.9.6](https://github.com/getkirby/kirby/releases/tag/3.9.6). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have fixed the affected code to only remove the Unicode BOM sequence at the beginning of the file. This fixes this vulnerability both for newly written as well as for existing content files.

### Credits

Thanks to Patrick Falb (@dapatrese) at [FORMER 03](https://former03.de/) for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-x5mr-p6v4-wp93
- https://nvd.nist.gov/vuln/detail/CVE-2023-38488
- https://github.com/getkirby/kirby/commit/a1e0f81c799ddae1af91cf37216f8ded9cb93540
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.5.8.3
- https://github.com/getkirby/kirby/releases/tag/3.6.6.3
- https://github.com/getkirby/kirby/releases/tag/3.7.5.2
- https://github.com/getkirby/kirby/releases/tag/3.8.4.1
- https://github.com/getkirby/kirby/releases/tag/3.9.6
