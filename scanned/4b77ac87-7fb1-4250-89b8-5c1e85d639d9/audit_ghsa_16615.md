# [M] Read private customer data reclaiming carts in Klaviyo Magento

## Summary
Severity: Medium
Advisory: GHSA-hvgw-gg3p-295j
CWE: CWE-200
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-hvgw-gg3p-295j
Type: github-advisory

## Affected
- Packagist: `klaviyo/magento2-extension` — affected >=1.0.0 <3.0.0

## Details
A researcher identified an endpoint in a thirth party module Klaviyo Magento 2 which allows to read private customer data from stores. It works by reclaiming any guest-cart as your own and reading the private data for the orders in the Magento API.

## References
- https://github.com/klaviyo/magento2-klaviyo/pull/107
- https://gist.github.com/JeroenBoersma/f5864a45e3df63b198a57abdff366df2
- https://github.com/FriendsOfPHP/security-advisories/blob/master/klaviyo/magento2-extension/2021-05-25-1.yaml
- https://github.com/klaviyo/magento2-klaviyo
