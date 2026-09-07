# [M] Kirby vulnerable to path traversal of collection names during file system lookup

## Summary
Severity: Medium
Advisory: GHSA-x275-h9j4-7p4h
CVE: CVE-2025-31493
CWE: CWE-22, CWE-23
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-05-13
Source: https://github.com/advisories/GHSA-x275-h9j4-7p4h
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <3.9.8.3
- Packagist: `getkirby/cms` — affected >=3.10.0 <3.10.1.2
- Packagist: `getkirby/cms` — affected >=4.0.0 <4.7.1

## Details
### TL;DR

This vulnerability affects all Kirby sites that use the `collection()` helper or `$kirby->collection()` method with a dynamic collection name (such as a collection name that depends on request or user data).

Sites that only use fixed calls to the `collection()` helper/`$kirby->collection()` method (i.e. calls with a simple string for the collection name) are *not* affected.

----

### Introduction

Kirby's `collection()` helper and `$kirby->collection()` method (in the following abbreviated to the `collection()` helper) allow to load PHP logic files that are normally stored in the `site/collections` folder or registered by plugins through the `collections` plugin extension.

If the `collection()` helper is called with an arbitrary collection name, Kirby first checks if a file with this name exists in the collections root (which defaults to `site/collections`).

This logic was vulnerable against path traversal attacks. By using special elements such as `..` and `/` separators, attackers can escape outside of the restricted location to access files or directories that are elsewhere on the system. One of the most common special elements is the `../` sequence, which in most modern operating systems is interpreted as the parent directory of the current location.

Because Kirby's `collection()` helper did not protect against path traversal, the provided collection name could include special sequences that would cause Kirby to look outside of the configured collections root and access arbitrary files.

### Impact

The missing path traversal check allowed attackers to navigate and access all files on the server that were accessible to the PHP process, including files outside of the collections root or even outside of the Kirby installation. PHP code within such files was executed.

Such attacks first require an attack vector in the site code that is caused by dynamic collection names, such as `collection('tags-' . get('tags'))`. It generally also requires knowledge of the site structure and the server's file system by the attacker, although it can be possible to find vulnerable setups through automated methods such as fuzzing.

In a vulnerable setup, this could cause damage to the confidentiality and integrity of the server, for example:

- it could allow the attacker to build a map of the server's file system for subsequent attacks,
- it could allow access to configuration files that may contain sensitive information like security tokens or
- it could cause the unintended execution of PHP scripts.

### Patches

The problem has been patched in [Kirby 3.9.8.3](https://github.com/getkirby/kirby/releases/tag/3.9.8.3), [Kirby 3.10.1.2](https://github.com/getkirby/kirby/releases/tag/3.10.1.2) and [Kirby 4.7.1](https://github.com/getkirby/kirby/releases/tag/4.7.1). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have added a check for the collection path that ensures that the resulting path is contained within the configured collections root. Collection paths that point outside of the collections root will not be loaded.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-x275-h9j4-7p4h
- https://nvd.nist.gov/vuln/detail/CVE-2025-31493
- https://github.com/getkirby/kirby/commit/95a51480a426a8ed0df799cc017403be9b987ced
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.10.1.2
- https://github.com/getkirby/kirby/releases/tag/3.9.8.3
- https://github.com/getkirby/kirby/releases/tag/4.7.1
