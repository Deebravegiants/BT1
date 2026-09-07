# [H] Kirby CMS has pre-authentication path traversal and PHP file inclusion during user lookup

## Summary
Severity: High
Advisory: GHSA-9hx7-c53c-v6x8
CVE: CVE-2026-44177
CWE: CWE-22, CWE-98
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-9hx7-c53c-v6x8
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=5.3.0 <5.4.1

## Details
### TL;DR

This vulnerability affects all Kirby sites on Kirby 5.3.0-5.4.0 and is independent from setup conditions and authentication.

**This vulnerability is of high severity for all Kirby sites**.

----

### Introduction

Path traversal is a type of attack that allows to access arbitrary filesystem paths. By using special elements such as `..` and `/` separators, attackers can escape outside of the restricted location to access files or directories that are elsewhere on the system. One of the most common special elements is the `../` sequence, which in most modern operating systems is interpreted as the parent directory of the current location. Path traversal can give attackers information about the filesystem and directory structure on the server and can lead to additional attacks depending on the nature of the accessible files and directories.

PHP file inclusion is a type of attack that allows to load and execute PHP files on the server that are not intended for direct inclusion. Depending on the logic inside the PHP files, this can lead to disclosure of sensitive information or unintended, malicious actions.

### Affected components

Kirby's `Users` collection received a performance improvement in Kirby 5.3.0. Starting in this release, Kirby loads user objects lazily when they are first needed. Users are queried by their user ID, which is then used to look up the user's account directory in the `site/accounts` directory.

This applies to the authentication API (accessible to unauthenticated requests), the users API (accessible to authenticated users only) as well as to other places that use `$users->find()` to look up an individual user with a request-provided email or user ID.

### Impact

In affected releases, Kirby did not correctly validate the provided user ID, causing a path traversal vulnerability. This vulnerability results in the following impact:

- Arbitrary PHP file inclusion of files with the filename `index.php` (e.g. the main PHP files of plugins), the impact of which depends on the contents and logic inside the includable files.
- Probing of the existence of arbitrary directories on the server, which can allow attackers to fingerprint the server and site setup, including installed plugins and the content structure.

### Patches

The problem has been patched in [Kirby 5.4.1](https://github.com/getkirby/kirby/releases/tag/5.4.1). Please update to this or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In the mentioned release, Kirby has added additional checks to the user lookup that ensure that the provided user ID only contains valid characters and that the resulting path to the account directory is contained in the `site/accounts` directory.

### Credits

Kirby thanks @offset for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-9hx7-c53c-v6x8
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/5.4.1
