# [M] Neos Flow Information disclosure in entity security

## Summary
Severity: Medium
Advisory: GHSA-9cw3-j7wg-jwj8
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-17
Source: https://github.com/advisories/GHSA-9cw3-j7wg-jwj8
Type: github-advisory

## Affected
- Packagist: `neos/flow` — affected >=3.0.0 <3.0.12
- Packagist: `neos/flow` — affected >=3.1.0 <3.1.10
- Packagist: `neos/flow` — affected >=3.2.0 <3.2.13
- Packagist: `neos/flow` — affected >=3.3.0 <3.3.13
- Packagist: `neos/flow` — affected >=4.0.0 <4.0.6

## Details
If you had used entity security and wanted to secure entities not just based on the user's role, but on some property of the user (like the company he belongs to), entity security did not work properly together with the doctrine query cache. This could lead to other users re-using SQL queries from the cache which were built for other users; and thus users could see entities which were not destined for them.

### Am I affected?

- Do you use Entity Security? if no, you are not affected.
- You disabled the Doctrine Cache (Flow_Persistence_Doctrine)? If this is the case, you are not affected.
- You use Entity Security in custom Flow or Neos applications. Read on.
  - If you only used Entity Security based on roles (i.e. role A was allowed to see entities, but role B was denied): In this case, you are not affected.
  - If you did more advanced stuff using Entity Security (like checking that a customer only sees his own orders; or a hotel only sees its own bookings), you very likely needed to register a custom global object in Neos.Flow.aop.globalObjects. In this case, you are affected by the issue; and need to implement the CacheAwareInterface in your global object for proper caching.

All Flow versions (starting in version 3.0, where Entity Security was introduced) were affected.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/neos/flow/2017-04-12.yaml
- https://github.com/neos/flow
- https://www.neos.io/blog/flow-bugfix-releases-for-entity-security.html
