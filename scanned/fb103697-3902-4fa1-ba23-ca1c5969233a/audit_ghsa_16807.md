# [M] FOSRestBundle issue with broken validation of JSONP callbacks

## Summary
Severity: Medium
Advisory: GHSA-p9fg-j6ww-953m
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-p9fg-j6ww-953m
Type: github-advisory

## Affected
- Packagist: `friendsofsymfony/rest-bundle` — affected >=1.2.0 <1.2.2

## Details
Starting with FOSRestBundle 1.2 we [switched](https://github.com/FriendsOfSymfony/FOSRestBundle/pull/642/files#diff-431bc57ca9ca16332c0cff43ad45263cR37) to using [willdurand/jsonp-callback-validator](https://github.com/willdurand/JsonpCallbackValidator) for validation of JSONP callbacks. However [the change was implemented](https://github.com/FriendsOfSymfony/FOSRestBundle/pull/665) incorrectly validating the callback query param name, rather than its value. Anyone using the JSONP handler (which is off by default) together with FOSRestBundle 1.2.0 or 1.2.1 should update to FOSRestBundle [1.2.2](https://github.com/FriendsOfSymfony/FOSRestBundle/releases/tag/1.2.2).

## References
- https://github.com/FriendsOfSymfony/FOSRestBundle/commit/3dd7d40068360c23366fb4884c5d194c769ec2c1
- https://github.com/FriendsOfPHP/security-advisories/blob/master/friendsofsymfony/rest-bundle/2014-01-22-1.yaml
- https://github.com/FriendsOfSymfony/FOSRestBundle
- https://symfony.com/blog/fosrestbundle-security-issue-with-jsonp-handler
