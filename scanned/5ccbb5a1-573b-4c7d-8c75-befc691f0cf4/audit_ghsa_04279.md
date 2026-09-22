# [M] symfony/ux-autocomplete: Information exposure via unescaped LIKE wildcards in EntitySearchUtil

## Summary
Severity: Medium
Advisory: GHSA-946h-jp5c-8fvh
CVE: CVE-2026-49211
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-946h-jp5c-8fvh
Type: github-advisory

## Affected
- Packagist: `symfony/ux-autocomplete` — affected >=2.2.0 <2.36.0
- Packagist: `symfony/ux-autocomplete` — affected >=3.0.0 <3.1.0

## Details
### Description

`Symfony\UX\Autocomplete\Doctrine\EntitySearchUtil::addSearchClause()` builds the `LIKE` expression used by the autocomplete endpoint by wrapping the client-supplied query in `%...%` without escaping the SQL `LIKE` wildcards (`%`, `_`, `\`). The value is passed as a bound parameter, so this is not SQL injection, but a client can send `%` to match every row or use `_` as a single-character wildcard.

Because `searchable_fields` defaults to every property of the entity and the autocomplete endpoint is public by default (`BaseEntityAutocompleteType` ships with `security => false`), an unauthenticated user can turn the endpoint into a broad matcher or a blind boolean oracle against every column of the entity, including columns the application never intended to expose.

### Resolution

`EntitySearchUtil` now escapes `\`, `%`, and `_` in the user-supplied query with `addcslashes()` and appends an explicit `ESCAPE '\'` clause to the generated `LIKE` expression, so those characters are matched literally. The exact-match `words_query` `IN()` branch is unchanged.

The patch for this issue is available [here](https://github.com/symfony/ux/commit/725ab3d40689c91ff19ad2d01940a30007769214) for branch 2.x (and forward-ported to 3.x).

### Credits

Symfony would like to thank Pascal Cescon for reporting the issue and providing the fix.

## References
- https://github.com/symfony/ux/security/advisories/GHSA-946h-jp5c-8fvh
- https://github.com/symfony/ux/commit/725ab3d40689c91ff19ad2d01940a30007769214
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/ux-autocomplete/CVE-2026-49211.yaml
- https://github.com/symfony/ux
