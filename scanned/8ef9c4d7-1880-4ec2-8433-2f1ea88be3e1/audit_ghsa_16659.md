# [M] amphp/http Host Header Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8v5x-6vv5-jv4g
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-8v5x-6vv5-jv4g
Type: github-advisory

## Affected
- Packagist: `amphp/http` — affected >=0 <1.0.1

## Details
amphp/http versions before 1.0.1 allows an attacker to supply invalid input in the Host header which may lead to various type of Host header injection attacks.

## References
- https://github.com/amphp/http/pull/4
- https://github.com/amphp/http/commit/16e465fa82555104d1cff98cb8e412295a380214
- https://github.com/FriendsOfPHP/security-advisories/blob/master/amphp/http/2018-03-15.yaml
- https://github.com/amphp/http
- https://github.com/amphp/http/releases/tag/v1.0.1
