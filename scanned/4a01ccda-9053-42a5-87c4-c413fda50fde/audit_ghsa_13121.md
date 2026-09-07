# [M] Prevent injection of invalid entity ids for "autocomplete" fields

## Summary
Severity: Medium
Advisory: GHSA-4cpv-669c-r79x
CVE: CVE-2023-41336
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-11
Source: https://github.com/advisories/GHSA-4cpv-669c-r79x
Type: github-advisory

## Affected
- Packagist: `symfony/ux-autocomplete` — affected >=0 <2.11.2

## Details
### Impact
Under certain circumstances, an attacker could successfully submit an entity id for an `EntityType` that is *not* part of the valid choices.

Affected applications are any that use:

* A custom `query_builder` option to limit the valid results;
AND
* An `EntityType` with `'autocomplete' => true` or a custom [AsEntityAutocompleteField](https://symfony.com/bundles/ux-autocomplete/current/index.html#usage-in-a-form-with-ajax).

Under this circumstance, if an id is submitted, it is accepted even if the matching record would not be returned by the custom query built with `query_builder`.

### Patches

The problem has been fixed in `symfony/ux-autocomplete` version 2.11.2.

### Workarounds
Upgrade to version 2.11.2 or greater of `symfony/ux-autocomplete` or perform extra validation after submit to verify the selected option is valid.

## References
- https://github.com/symfony/ux-autocomplete/security/advisories/GHSA-4cpv-669c-r79x
- https://nvd.nist.gov/vuln/detail/CVE-2023-41336
- https://github.com/symfony/ux-autocomplete/commit/fabcb2eee14b9e84a45b276711853a560b5d770c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/ux-autocomplete/CVE-2023-41336.yaml
- https://github.com/symfony/ux-autocomplete
- https://symfony.com/bundles/ux-autocomplete/current/index.html#usage-in-a-form-with-ajax
