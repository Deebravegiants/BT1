# [M] Kirby vulnerable to path traversal of snippet names in the `snippet()` helper

## Summary
Severity: Medium
Advisory: GHSA-fw82-87p8-v6hp
CVE: CVE-2025-30159
CWE: CWE-22, CWE-23
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-05-13
Source: https://github.com/advisories/GHSA-fw82-87p8-v6hp
Type: github-advisory

## Affected
- Packagist: `getkirby/kirby` — affected >=0 <3.9.8.3
- Packagist: `getkirby/kirby` — affected >=3.10.0 <3.10.1.2
- Packagist: `getkirby/kirby` — affected >=4.0.0 <4.7.1

## Details
### TL;DR

This vulnerability affects all Kirby sites that use the `snippet()` helper or `$kirby->snippet()` method with a dynamic snippet name (such as a snippet name that depends on request or user data).

Sites that only use fixed calls to the `snippet()` helper/`$kirby->snippet()` method (i.e. calls with a simple string for the snippet name) are *not* affected.

----

### Introduction

Kirby's `snippet()` helper and `$kirby->snippet()` method (in the following abbreviated to the `snippet()` helper) allow to load PHP snippet files that are normally stored in the `site/snippets` folder or registered by plugins through the `snippets` plugin extension.

If the `snippet()` helper is called with an arbitrary snippet name, Kirby first checks if a file with this name exists in the snippets root (which defaults to `site/snippets`).

This logic was vulnerable against path traversal attacks. By using special elements such as `..` and `/` separators, attackers can escape outside of the restricted location to access files or directories that are elsewhere on the system. One of the most common special elements is the `../` sequence, which in most modern operating systems is interpreted as the parent directory of the current location.

Because Kirby's `snippet()` helper did not protect against path traversal, the provided snippet name could include special sequences that would cause Kirby to look outside of the configured snippets root and access arbitrary files.

### Impact

The missing path traversal check allowed attackers to navigate and access all files on the server that were accessible to the PHP process, including files outside of the snippets root or even outside of the Kirby installation. PHP code within such files was executed.

Such attacks first require an attack vector in the site code that is caused by dynamic snippet names, such as `snippet('tags-' . get('tags'))`. It generally also requires knowledge of the site structure and the server's file system by the attacker, although it can be possible to find vulnerable setups through automated methods such as fuzzing.

In a vulnerable setup, this could cause damage to the confidentiality and integrity of the server, for example:

- it could allow the attacker to build a map of the server's file system for subsequent attacks,
- it could allow access to configuration files that may contain sensitive information like security tokens or
- it could cause the unintended execution of PHP scripts.

### Patches

The problem has been patched in [Kirby 3.9.8.3](https://github.com/getkirby/kirby/releases/tag/3.9.8.3), [Kirby 3.10.1.2](https://github.com/getkirby/kirby/releases/tag/3.10.1.2) and [Kirby 4.7.1](https://github.com/getkirby/kirby/releases/tag/4.7.1). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have added a check for the snippet path that ensures that the resulting path is contained within the configured snippets root. Snippet paths that point outside of the snippets root will not be loaded.

### Effects on site code

If you deliberately use path traversal in your projects, these uses will break after updating to one of the patched versions.

Examples of such uses include:

- Aliasing a template by loading another template with `snippet('../templates/other-template')`. Robust alternatives are to use `require __DIR__ . '/other-template.php'` or to override the `$page->template()` method in the page model:
  ```php
  class AnotherPage extends Page
  {
    public function template(): Template
    {
      return $this->kirby()->template('other-template');
    }
  }
  ```
- Loading a snippet from a shared directory in a multisite setup. A robust alternative is to restructure the project so that all sites share a single snippets root that then branches off into subdirectories for each site. If you prefer to keep the original structure, you can use symbolic links (symlinks) in the file system to include the shared directory in the site-specific snippets roots.

### Credits

Thanks to Bruno Meilick (@bnomei) for reporting the identified issue.
Thanks to Bruno Meilick and Tobias Möritz (@tobimori) for their input on the effects on site code.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-fw82-87p8-v6hp
- https://nvd.nist.gov/vuln/detail/CVE-2025-30159
- https://github.com/getkirby/kirby/commit/90acf7ed6d8d9d0697f938edc0940b4a563ddbe7
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.10.1.2
- https://github.com/getkirby/kirby/releases/tag/3.9.8.3
- https://github.com/getkirby/kirby/releases/tag/4.7.1
