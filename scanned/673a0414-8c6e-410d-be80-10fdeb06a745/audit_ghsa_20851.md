# [H] Pageflow vulnerable to insecure direct object reference in membership update endpoint

## Summary
Severity: High
Advisory: GHSA-qcqv-38jg-2r43
Ecosystem: RubyGems
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-qcqv-38jg-2r43
Type: github-advisory

## Affected
- RubyGems: `pageflow` — affected >=0 <14.5.2
- RubyGems: `pageflow` — affected >=15.0.0 <15.7.1

## Details
### Impact

Pageflow has a membership edit feature which allows users to edit the roles of user memberships associated with an account that they have the `manager` role to (including their own). While the `Entity` dropdown select field is greyed out in the UI, an attacker can use tools which allow sending arbitrary HTTP request to craft a request to the `/admin/users/{user_id}/memberships/{membership_id}` endpoint containing an additional `membership[entity_id]` parameter. This parameter is honored when the membership is updated, allowing an attacker to update the membership object associated with their own account (with `manager` role) to be associated with a different attacker-chosen account instead. Since `account_id`s are enumerable, an attacker can compromise all accounts present on the platform.

### Mitigation

Upgrade to version 15.7.1 or 14.5.2 of the `pageflow` gem.

### For more information

If you have any questions or comments about this advisory email us at info(at)codevise.de 

### Credits

[Positive Security](https://positive.security/)

## References
- https://github.com/codevise/pageflow/security/advisories/GHSA-qcqv-38jg-2r43
- https://github.com/codevise/pageflow/pull/1862
- https://github.com/codevise/pageflow
