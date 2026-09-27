# [H] Spree API has Unauthenticated IDOR - Guest Address

## Summary
Severity: High
Advisory: GHSA-3ghg-3787-w2xr
CVE: CVE-2026-22589
CWE: CWE-639
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-3ghg-3787-w2xr
Type: github-advisory

## Affected
- RubyGems: `spree_core` — affected >=4.0.0 <4.10.2
- RubyGems: `spree_core` — affected >=5.0.0 <5.0.7
- RubyGems: `spree_core` — affected >=5.1.0 <5.1.9
- RubyGems: `spree_core` — affected >=5.2.0 <5.2.5

## Details
### Summary
An Unauthenticated Insecure Direct Object Reference (IDOR) vulnerability was identified that allows an unauthenticated attacker to access guest address information without supplying valid credentials or session cookies.

### Details
During testing, it was observed that all guest users can make an unauthenticated request to retrieve address data belonging to other guest users by manipulating object identifiers. The attacker would need to know the storefront URL structure to perform this attack (which can be learnt after creating a registered user account).

Affected Component(s)
* Address Edit endpoint: `/addresses/{addressId}/edit`

Root Cause
- Faulty authorization check in CanCanCan Ability class:

```diff
- can :manage, ::Spree::Address, user_id: user.id
+ can :manage, ::Spree::Address, user_id: user.id if user.persisted?
```

the `user` object in `Spree::Ability` class for guest users is a `Spree.user_class.new` object. 

Addresses endpoint to access it is part of the `spree_storefront` gem. **Headless builds using APIs are not affected,** as the Addresses endpoint there is only for registered users, and records are scoped to the currently signed-in user.

### PoC
Preconditions
- No authentication required
- No cookies or session tokens set

To reproduce this vulnerability simply perform the request shown below, replacing the number with an arbitrary value. 

**For the initial request the Guest Address id = 6 is used to obtain the information**

**Request**
GET `/addresses/6/edit`

<img width="291" height="454" alt="IDOR Guest" src="https://github.com/user-attachments/assets/d21d01a2-8fa5-4ab1-b9e2-6ee65bd6b5a2" />

Repeat the request and check the response, in this example using Guest Address id = 2.

**Request**
GET `/addresses/2/edit`

[<img width="360" height="519" alt="IDOR Guest Address ID 2" src="https://github.com/user-attachments/assets/1ce35990-3d11-4f47-9bba-266b5361313c" />
](url)

### Impact
An unauthenticated attacker can:

- Enumerate and retrieve guest address information (Addresses associated with User accounts are NOT affected)
- Access personally identifiable information (PII) such as:
- Full names
- Physical addresses
- Phone numbers (if present)

This vulnerability could lead to:

- Privacy violations
- Regulatory compliance issues (e.g., GDPR)
- Loss of user trust

## References
- https://github.com/spree/spree/security/advisories/GHSA-3ghg-3787-w2xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-22589
- https://github.com/spree/spree/commit/16067def6de8e0742d55313e83b0fbab6d2fd795
- https://github.com/spree/spree/commit/4c2bd62326fba0d846fd9e4bad2c62433829b3ad
- https://github.com/spree/spree/commit/d051925778f24436b62fa8e4a6b842c72ca80a67
- https://github.com/spree/spree/commit/e1cff4605eb15472904602aebaf8f2d04852d6ad
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spree_core/CVE-2026-22589.yml
- https://github.com/spree/spree
