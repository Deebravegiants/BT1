# [H] Pageflow vulnerable to sensitive user data extraction via Ransack query injection

## Summary
Severity: High
Advisory: GHSA-wrrw-crp8-979q
Ecosystem: RubyGems
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-wrrw-crp8-979q
Type: github-advisory

## Affected
- RubyGems: `pageflow` — affected >=0 <14.5.2
- RubyGems: `pageflow` — affected >=15.0.0 <15.7.1

## Details
### Impact

The attack allows extracting sensitive properties of database objects that are associated with users or entries belonging to an account that the attacker has access to.

Pageflow uses the `ActiveAdmin` Ruby library to provide some management features to its users. `ActiveAdmin` relies on the `Ransack` library to implement search functionality. In its default configuration, `Ransack` will allow for query conditions based on properties of associated database objects [1]. The `*_starts_with`, `*_ends_with` or `*_contains` search matchers [2] can then be abused to exfiltrate sensitive string values of associated database objects via character-by-character brute-force.

[1] https://activerecord-hackery.github.io/ransack/going-further/associations/
[2] https://activerecord-hackery.github.io/ransack/getting-started/search-matches/

### Mitigation

Upgrade to version 15.7.1 or 14.5.2 of the `pageflow` gem.

### For more information

If you have any questions or comments about this advisory email us at info(at)codevise.de 

### Credits

[Positive Security](https://positive.security/)

## References
- https://github.com/codevise/pageflow/security/advisories/GHSA-wrrw-crp8-979q
- https://github.com/codevise/pageflow/pull/1862
- https://github.com/codevise/pageflow
