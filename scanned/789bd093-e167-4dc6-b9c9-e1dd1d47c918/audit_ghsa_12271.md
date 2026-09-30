# [M] Spree Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jxx8-v83v-rhw3
CVE: CVE-2013-1656
CWE: CWE-20
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-jxx8-v83v-rhw3
Type: github-advisory

## Affected
- RubyGems: `spree` — affected >=1.0.0 <2.0.0.rc1

## Details
Spree Commerce 1.0.x before 2.0.0.rc1 allows remote authenticated administrators to instantiate arbitrary Ruby objects and execute arbitrary commands via the (1) `payment_method` parameter to `core/app/controllers/spree/admin/payment_methods_controller.rb`; and the (2) `promotion_action parameter` to `promotion_actions_controller.rb`, (3) `promotion_rule parameter` to `promotion_rules_controller.rb`, and (4) `calculator_type` parameter to `promotions_controller.rb` in `promo/app/controllers/spree/admin/`, related to unsafe use of the constantize function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1656
- https://github.com/spree/spree/commit/70092eb55b8be8fe5d21a7658b62da658612fba7
- https://blog.convisoappsec.com/en/spree-commerce-multiple-unsafe-reflection-vulnerabilities-cve-2013-1656
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spree/CVE-2013-1656.yml
- https://github.com/spree/spree
- https://web.archive.org/web/20130907044454/https://www.conviso.com.br/advisories/CVE-2013-1656.txt
- https://web.archive.org/web/20140329142330/http://spreecommerce.com/blog/multiple-security-vulnerabilities-fixed
- https://web.archive.org/web/20140618100330/http://blog.conviso.com.br/2013/03/spree-commerce-multiple-unsafe.html
