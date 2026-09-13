# [H] MagicLink: Insecure Deserialization of MagicLink Actions Leads to Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-r33w-fg8j-9c94
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-r33w-fg8j-9c94
Type: github-advisory

## Affected
- Packagist: `cesargb/laravel-magiclink` — affected >=2.0.0 <2.25.1

## Details
## Description

MagicLink stores serialized action objects in the `magic_links.action` database column and deserializes them without integrity validation or class allowlisting in [src/MagicLink.php](src/MagicLink.php#L59-L77) and [src/Actions/ResponseAction.php](src/Actions/ResponseAction.php#L64-L77). An attacker with the ability to manipulate database records (e.g., via SQL injection or compromised admin access) could inject malicious serialized objects containing arbitrary closures, leading to Remote Code Execution (RCE) when the magic link is visited.

## Resolution

The vulnerability has been mitigated through HMAC-signed serialization using the application key, class allowlisting restricted to `ActionAbstract` subclasses and framework classes, strict type validation preventing arbitrary object storage, and backward compatibility support for legacy data via `allowed_classes` in `unserialize()`. Implementation includes a new [Serializable](src/Security/Serializable/Serializable.php) security class with signing/verification, refactored getter/setter methods in MagicLink.

## References
- https://github.com/cesargb/laravel-magiclink/security/advisories/GHSA-r33w-fg8j-9c94
- https://github.com/cesargb/laravel-magiclink
- https://github.com/cesargb/laravel-magiclink/releases/tag/v2.25.1
