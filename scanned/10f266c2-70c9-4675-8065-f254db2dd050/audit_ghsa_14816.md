# [H] Zendframework Remote Address Spoofing Vector in `Zend\Http\PhpEnvironment\RemoteAddress`

## Summary
Severity: High
Advisory: GHSA-xffp-6w68-4775
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-xffp-6w68-4775
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=2.2.0 <2.2.5

## Details
The `Zend\Http\PhpEnvironment\RemoteAddress` class provides features around detecting the internet protocol (IP) address for an incoming proxied request via the X-Forwarded-For header, taking into account a provided list of trusted proxy server IPs. Prior to 2.2.5, the class was not taking into account whether or not the IP address contained in PHP's `$_SERVER['REMOTE_ADDR']` was in the trusted proxy server list.

The IETF draft specification indicates that if `$_SERVER['REMOTE_ADDR']` is not a trusted proxy, it must be considered the originating IP address, and the value of X-Forwarded-For must be disregarded.

## References
- https://github.com/zendframework/zendframework/commit/bb6784461d3b23ef1db4be8cf47957ccc3b681ed
- https://framework.zend.com/security/advisory/ZF2013-04
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/ZF2013-04.yaml
- https://github.com/zendframework/zendframework
