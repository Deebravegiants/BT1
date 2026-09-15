# [H] EasyAdmin custom-action dispatcher bypasses access_control on other routes

## Summary
Severity: High
Advisory: GHSA-g2fm-8hr4-j82h
CVE: CVE-2026-81892
CWE: CWE-639, CWE-862, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-g2fm-8hr4-j82h
Type: github-advisory

## Affected
- Packagist: `easycorp/easyadmin-bundle` — affected >=4.0.0 <4.29.16
- Packagist: `easycorp/easyadmin-bundle` — affected >=5.0.0 <5.5.1

## Details
## Summary

EasyAdmin serves all backend requests through a single dashboard route and, for custom actions (`Action::linkToRoute()` / `MenuItem::linkToRoute()`), swaps the executed controller based on the `routeName` query parameter on the `kernel.controller` event.

That swap happens **after** Symfony's security firewall has already evaluated `access_control` against the original dashboard URL, and the `routeName` value was not validated. As a result, a path-based `access_control` rule protecting the *target* route was never evaluated, so a low-privilege backend user could reach a more restricted route by name.

## Impact

Any application where `access_control` (or another path-based Symfony security rule) protects some routes more strictly than the dashboard URL used to reach EasyAdmin. An attacker who can reach a single EasyAdmin URL and knows a target route's **name** can execute that route's controller, bypassing the path-based rule.

Only **path-based** protections are bypassed. Routes whose controller enforces its own authorization with `#[IsGranted]` / `denyAccessUnlessGranted()` remain protected, because those checks are recomputed against the swapped-in controller.

## Patches

Fixed in **4.29.16** and **5.5.1**. Before dispatching a custom-action route, EasyAdmin now re-evaluates the target route's `access_control` rule and denies the request if the current user is not granted access.

## Workarounds

Add controller-level authorization (`#[IsGranted]` / `denyAccessUnlessGranted()`) to any sensitive route, since controller-level checks are still enforced. Upgrading is the recommended fix.

## Credits

Reported by @TungNGo02.

## References
- https://github.com/EasyCorp/EasyAdminBundle/security/advisories/GHSA-g2fm-8hr4-j82h
- https://nvd.nist.gov/vuln/detail/CVE-2026-81892
- https://github.com/EasyCorp/EasyAdminBundle/commit/03be45c6b7213c4c984a1d0542b7ec60359329f8
- https://github.com/EasyCorp/EasyAdminBundle/commit/6228dfef598d81eeb0baa35625e50812f3c77699
- https://github.com/EasyCorp/EasyAdminBundle
- https://github.com/EasyCorp/EasyAdminBundle/releases/tag/v4.29.16
- https://github.com/EasyCorp/EasyAdminBundle/releases/tag/v5.5.1
- https://github.com/FriendsOfPHP/security-advisories/blob/master/easycorp/easyadmin-bundle/CVE-2026-81892.yaml
