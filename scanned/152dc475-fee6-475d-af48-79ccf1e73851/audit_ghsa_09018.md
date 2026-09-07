# [H] Kirby CMS has an Arbitrary Method Call via REST API Search and Collection Query Endpoints

## Summary
Severity: High
Advisory: GHSA-86rh-h242-j8xp
CVE: CVE-2026-44174
CWE: CWE-470
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-86rh-h242-j8xp
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.1
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.4.1

## Details
### TL;DR

This vulnerability affects all Kirby sites that might have potential attackers in the group of authenticated Panel users.

**This vulnerability is of high severity for affected sites and has a high real-world impact.**

----

### Introduction

Arbitrary method call is a type of arbitrary code execution. It is a vulnerability that allows attackers to run any commands or code of the attacker's choice on a target machine or in a target process.

Depending on the set of accessible methods, this can lead to disclosure of sensitive information or to unintended and malicious write actions.

### Affected components

Kirby's data model is made up of model objects that are contained in collection objects. These collections can be queried with methods such as `$collection->filter()`, `$collection->sort()`, `$collection->group()`, `$collection->pluck()` and `$collection->findBy()`. Each of these methods allows to query the models contained in the collection by any accessible model attribute (field or method).

Kirby also provides endpoints in its REST API that allow to search through users or through children and files of the site or of a particular page. These endpoints allow the `search`, `not`, `filter` and `sort` queries as well as options to paginate the result. The same kind of queries can also be provided to API collections such as `/<site|page|user>/blueprints`, `/<site|page>/children`, `/<model>/files`, `/languages`, `/roles`, `/translations`, `/users` and `/<user>/roles`.

### Impact

In affected releases, Kirby did not validate the model attributes that were used in the collection queries. This allowed attackers to include arbitrary model methods in their queries. This includes methods with sensitive data such as `password()` (disclosing the password hash) or `root()` (disclosing the absolute filesystem path on the server) as well as methods that perform impactful actions such as `loginPasswordless()` (causing a privilege escalation to another user) or `delete()` (deleting all queried models in one go if the authenticated user has appropriate permissions).

### Patches

The problem has been patched in [Kirby 4.9.1](https://github.com/getkirby/kirby/releases/tag/4.9.1) and [Kirby 5.4.1](https://github.com/getkirby/kirby/releases/tag/5.4.1). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, Kirby has added a blocklist of sensitive model methods that should not be called during collection operations and limited the query options for the affected endpoints to search and pagination.

### Credits

Kirby thanks @mojamojam for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-86rh-h242-j8xp
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.1
- https://github.com/getkirby/kirby/releases/tag/5.4.1
