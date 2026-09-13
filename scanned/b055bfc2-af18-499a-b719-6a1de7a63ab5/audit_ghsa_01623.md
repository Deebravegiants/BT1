# [H] Authorization bypass in Spree

## Summary
Severity: High
Advisory: GHSA-m2jr-hmc3-qmpr
CVE: CVE-2020-26223
CWE: CWE-863
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-11-13
Source: https://github.com/advisories/GHSA-m2jr-hmc3-qmpr
Type: github-advisory

## Affected
- RubyGems: `spree_api` — affected >=3.7.0 <3.7.13
- RubyGems: `spree_api` — affected >=4.0.0 <4.0.5
- RubyGems: `spree_api` — affected >=4.1.0 <4.1.12

## Details
### Impact
The perpetrator could query the [API v2 Order Status](https://guides.spreecommerce.org/api/v2/storefront#tag/Order-Status) endpoint with an empty string passed as an Order token

### Patches
Please upgrade to 3.7.11, 4.0.4, or 4.1.11 depending on your used Spree version. Users of Spree < 3.7 are not affected.

### References
Pull request with a fix and in-depth explanation - https://github.com/spree/spree/pull/10573

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@spreecommerce.org](mailto:security@spreecommerce.org)

## References
- https://github.com/spree/spree/security/advisories/GHSA-m2jr-hmc3-qmpr
- https://nvd.nist.gov/vuln/detail/CVE-2020-26223
- https://github.com/spree/spree/pull/10573
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spree_api/CVE-2020-26223.yml
- https://github.com/spree/spree
- https://guides.spreecommerce.org/api/v2/storefront#tag/Order-Status
- https://rubygems.org/gems/spree_api/versions
